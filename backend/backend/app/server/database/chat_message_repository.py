"""Chat message repository for managing chat message CRUD operations"""
from typing import List, Optional, Tuple

from backend.app.server.database.db_session import get_db_connection, TABLE_CHAT_MESSAGES
from backend.app.server.database.models.chat_session_models import Message, MessageCreate, MessageUpdate
from backend.app.utils.logger_util import log_info, log_error, log_debug


class ChatMessageRepository:
    """Repository for managing chat message database operations"""

    @staticmethod
    def create_message(message_create: MessageCreate) -> str:
        """
        Create a new message in a chat session.

        Args:
            message_create: MessageCreate model containing message data

        Returns:
            The message_id of the newly created message

        Raises:
            Exception: If message creation fails
        """
        try:
            conn = get_db_connection()

            conn.execute(f"""
                INSERT INTO {TABLE_CHAT_MESSAGES} (
                    message_id, chat_session_id, utc_time, sender, receiver,
                    messages, mode, content_type, message_type, file_name, file_path, mime_type, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, [
                message_create.message_id,
                message_create.chat_session_id,
                message_create.utc_time,
                message_create.sender,
                message_create.receiver,
                message_create.messages,
                message_create.mode,
                message_create.content_type,
                message_create.message_type,
                message_create.file_name,
                message_create.file_path,
                message_create.mime_type
            ])

            conn.close()
            log_info(
                f"Created new message: {message_create} ")
            return message_create.message_id

        except Exception as e:
            log_error(f"Error creating message: {e}")
            raise

    @staticmethod
    def get_message_by_id(message_id: str) -> Optional[Message]:
        """
        Get a message by its ID.

        Args:
            message_id: The ID of the message to retrieve

        Returns:
            Message model or None if not found
        """
        try:
            conn = get_db_connection()

            result = conn.execute(f"""
                SELECT message_id, chat_session_id, utc_time, sender, receiver,
                       messages, mode, created_at, content_type, message_type, 
                       file_name, file_path, mime_type
                FROM {TABLE_CHAT_MESSAGES}
                WHERE message_id = ?
            """, [message_id]).fetchone()

            conn.close()

            if result:
                return Message(
                    message_id=result[0],
                    chat_session_id=result[1],
                    utc_time=result[2],
                    sender=result[3],
                    receiver=result[4],
                    messages=result[5],
                    mode=result[6],
                    created_at=result[7],
                    content_type=result[8],
                    message_type=result[9],
                    file_name=result[10],
                    file_path=result[11],
                    mime_type=result[12]
                )
            return None

        except Exception as e:
            log_error(f"Error getting message by ID {message_id}: {e}")
            raise

    @staticmethod
    def get_messages_by_chat_session(
            chat_session_id: str,
            page: int = 0,
            page_size: int = 20,
            reversed: bool = True
    ) -> Tuple[List[Message], int]:
        """
        Get messages for a specific chat session with pagination.

        Args:
            chat_session_id: The ID of the chat session
            page: Page number (0-based)
            page_size: Number of messages per page (default: 20)

        Returns:
            Tuple of (List of Message models, total count)
        """
        try:
            conn = get_db_connection()

            # Calculate offset
            offset = (page) * page_size

            # Get total count
            count_result = conn.execute(f"""
                SELECT COUNT(*) FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ?
            """, [chat_session_id]).fetchone()
            total_count = count_result[0] if count_result else 0

            # Get paginated messages
            results = conn.execute(f"""
                SELECT message_id, chat_session_id, utc_time, sender, receiver,
                       messages, mode, created_at, content_type, message_type,
                       file_name, file_path, mime_type
                FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, [chat_session_id, page_size, offset]).fetchall()

            conn.close()

            messages = []
            for row in results:
                messages.append(Message(
                    message_id=row[0],
                    chat_session_id=row[1],
                    utc_time=row[2],
                    sender=row[3],
                    receiver=row[4],
                    messages=row[5],
                    mode=row[6],
                    created_at=row[7],
                    content_type=row[8],
                    message_type=row[9],
                    file_name=row[10],
                    file_path=row[11],
                    mime_type=row[12]
                ))
            log_debug(messages)
            log_debug(f"Retrieved {len(messages)} messages for chat session {chat_session_id} (page {page})")
            return messages, total_count

        except Exception as e:
            log_error(f"Error getting messages for chat session {chat_session_id}: {e}")
            raise

    @staticmethod
    def get_all_messages_by_chat_session(chat_session_id: str) -> List[Message]:
        """
        Get all messages for a specific chat session without pagination.

        Args:
            chat_session_id: The ID of the chat session

        Returns:
            List of Message models
        """
        try:
            conn = get_db_connection()

            results = conn.execute(f"""
                SELECT message_id, chat_session_id, utc_time, sender, receiver,
                       messages, mode, created_at, content_type, message_type,
                       file_name, file_path, mime_type
                FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ?
                ORDER BY created_at ASC
            """, [chat_session_id]).fetchall()

            conn.close()

            messages = []
            for row in results:
                messages.append(Message(
                    message_id=row[0],
                    chat_session_id=row[1],
                    utc_time=row[2],
                    sender=row[3],
                    receiver=row[4],
                    messages=row[5],
                    mode=row[6],
                    created_at=row[7],
                    content_type=row[8],
                    message_type=row[9],
                    file_name=row[10],
                    file_path=row[11],
                    mime_type=row[12]
                ))

            log_debug(f"Retrieved {len(messages)} messages for chat session {chat_session_id}")
            return messages

        except Exception as e:
            log_error(f"Error getting all messages for chat session {chat_session_id}: {e}")
            raise

    @staticmethod
    def update_message(message_id: str, message_update: MessageUpdate) -> bool:
        """
        Update a message.

        Args:
            message_id: The ID of the message to update
            message_update: MessageUpdate model with fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            if message_update.messages is not None:
                conn.execute(f"""
                    UPDATE {TABLE_CHAT_MESSAGES}
                    SET messages = ?
                    WHERE message_id = ?
                """, [message_update.messages, message_id])

                conn.close()
                log_info(f"Updated message {message_id}")
                return True
            else:
                log_debug(f"No fields to update for message {message_id}")
                return True

        except Exception as e:
            log_error(f"Error updating message {message_id}: {e}")
            return False

    @staticmethod
    def delete_message(message_id: str) -> bool:
        """
        Permanently delete a message.

        Args:
            message_id: The ID of the message to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            conn.execute(f"DELETE FROM {TABLE_CHAT_MESSAGES} WHERE message_id = ?", [message_id])

            conn.close()
            log_info(f"Deleted message {message_id}")
            return True

        except Exception as e:
            log_error(f"Error deleting message {message_id}: {e}")
            return False

    @staticmethod
    def delete_messages_by_chat_session(chat_session_id: str) -> bool:
        """
        Delete all messages for a specific chat session.

        Args:
            chat_session_id: The ID of the chat session

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            conn.execute(f"""
                DELETE FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ?
            """, [chat_session_id])

            conn.close()
            log_info(f"Deleted all messages for chat session {chat_session_id}")
            return True

        except Exception as e:
            log_error(f"Error deleting messages for chat session {chat_session_id}: {e}")
            return False

    @staticmethod
    def get_message_count_by_chat_session(chat_session_id: str) -> int:
        """
        Get the total count of messages in a chat session.

        Args:
            chat_session_id: The ID of the chat session

        Returns:
            Total number of messages
        """
        try:
            conn = get_db_connection()

            result = conn.execute(f"""
                SELECT COUNT(*) FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ?
            """, [chat_session_id]).fetchone()

            conn.close()

            count = result[0] if result else 0
            log_debug(f"Message count for chat session {chat_session_id}: {count}")
            return count

        except Exception as e:
            log_error(f"Error getting message count for chat session {chat_session_id}: {e}")
            return 0

    @staticmethod
    def get_latest_messages(
            chat_session_id: str,
            limit: int = 10
    ) -> List[Message]:
        """
        Get the latest N messages from a chat session.

        Args:
            chat_session_id: The ID of the chat session
            limit: Number of latest messages to retrieve

        Returns:
            List of Message models (latest first)
        """
        try:
            conn = get_db_connection()

            results = conn.execute(f"""
                SELECT message_id, chat_session_id, utc_time, sender, receiver,
                       messages, mode, created_at, content_type, message_type,
                       file_name, file_path, mime_type
                FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, [chat_session_id, limit]).fetchall()

            conn.close()

            messages = []
            for row in results:
                messages.append(Message(
                    message_id=row[0],
                    chat_session_id=row[1],
                    utc_time=row[2],
                    sender=row[3],
                    receiver=row[4],
                    messages=row[5],
                    mode=row[6],
                    created_at=row[7],
                    content_type=row[8],
                    message_type=row[9],
                    file_name=row[10],
                    file_path=row[11],
                    mime_type=row[12]
                ))

            log_debug(f"Retrieved {len(messages)} latest messages for chat session {chat_session_id}")
            return messages

        except Exception as e:
            log_error(f"Error getting latest messages for chat session {chat_session_id}: {e}")
            raise

    @staticmethod
    def search_messages(
            chat_session_id: str,
            search_term: str,
            page: int = 1,
            page_size: int = 20
    ) -> Tuple[List[Message], int]:
        """
        Search messages in a chat session by content.

        Args:
            chat_session_id: The ID of the chat session
            search_term: Text to search for in message content
            page: Page number (1-based)
            page_size: Number of messages per page (default: 20)

        Returns:
            Tuple of (List of Message models, total count)
        """
        try:
            conn = get_db_connection()

            # Calculate offset
            offset = (page - 1) * page_size
            search_pattern = f"%{search_term}%"

            # Get total count
            count_result = conn.execute(f"""
                SELECT COUNT(*) FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ? AND messages LIKE ?
            """, [chat_session_id, search_pattern]).fetchone()
            total_count = count_result[0] if count_result else 0

            # Get paginated search results
            results = conn.execute(f"""
                SELECT message_id, chat_session_id, utc_time, sender, receiver,
                       messages, mode, created_at, content_type, message_type,
                       file_name, file_path, mime_type
                FROM {TABLE_CHAT_MESSAGES}
                WHERE chat_session_id = ? AND messages LIKE ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, [chat_session_id, search_pattern, page_size, offset]).fetchall()

            conn.close()

            messages = []
            for row in results:
                messages.append(Message(
                    message_id=row[0],
                    chat_session_id=row[1],
                    utc_time=row[2],
                    sender=row[3],
                    receiver=row[4],
                    messages=row[5],
                    mode=row[6],
                    created_at=row[7],
                    content_type=row[8],
                    message_type=row[9],
                    file_name=row[10],
                    file_path=row[11],
                    mime_type=row[12]
                ))

            log_debug(f"Found {len(messages)} messages matching '{search_term}' in chat session {chat_session_id}")
            return messages, total_count

        except Exception as e:
            log_error(f"Error searching messages in chat session {chat_session_id}: {e}")
            raise
