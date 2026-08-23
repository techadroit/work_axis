"""Chat message repository for managing chat message CRUD operations"""
from typing import List, Optional, Tuple

from sqlalchemy import select, func

from src.app.server.database.db_session import get_db_session
from src.app.server.database.orm_models import ChatMessageORM
from src.app.server.database.models.chat_session_models import Message, MessageCreate, MessageUpdate
from src.app.utils.logger_util import log_info, log_error, log_debug


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
            with get_db_session() as session:
                message = ChatMessageORM(
                    message_id=message_create.message_id,
                    chat_session_id=message_create.chat_session_id,
                    utc_time=message_create.utc_time,
                    sender=message_create.sender,
                    receiver=message_create.receiver,
                    messages=message_create.messages,
                    mode=message_create.mode,
                    content_type=message_create.content_type,
                    message_type=message_create.message_type,
                    file_name=message_create.file_name,
                    file_path=message_create.file_path,
                    mime_type=message_create.mime_type,
                )
                session.add(message)

            log_info(f"Created new message: {message_create} ")
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
            with get_db_session() as session:
                message = session.get(ChatMessageORM, message_id)
                return Message.model_validate(message) if message else None

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
            offset = page * page_size

            with get_db_session() as session:
                total_count = session.execute(
                    select(func.count()).select_from(ChatMessageORM).where(
                        ChatMessageORM.chat_session_id == chat_session_id
                    )
                ).scalar_one()

                results = session.execute(
                    select(ChatMessageORM)
                    .where(ChatMessageORM.chat_session_id == chat_session_id)
                    .order_by(ChatMessageORM.created_at.desc())
                    .limit(page_size)
                    .offset(offset)
                ).scalars().all()

                messages = [Message.model_validate(row) for row in results]

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
            with get_db_session() as session:
                results = session.execute(
                    select(ChatMessageORM)
                    .where(ChatMessageORM.chat_session_id == chat_session_id)
                    .order_by(ChatMessageORM.created_at.asc())
                ).scalars().all()

                messages = [Message.model_validate(row) for row in results]

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
            if message_update.messages is None:
                log_debug(f"No fields to update for message {message_id}")
                return True

            with get_db_session() as session:
                message = session.get(ChatMessageORM, message_id)
                if message is None:
                    log_debug(f"Message {message_id} not found for update")
                    return True
                message.messages = message_update.messages

            log_info(f"Updated message {message_id}")
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
            with get_db_session() as session:
                session.execute(
                    ChatMessageORM.__table__.delete().where(ChatMessageORM.message_id == message_id)
                )

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
            with get_db_session() as session:
                session.execute(
                    ChatMessageORM.__table__.delete().where(
                        ChatMessageORM.chat_session_id == chat_session_id
                    )
                )

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
            with get_db_session() as session:
                count = session.execute(
                    select(func.count()).select_from(ChatMessageORM).where(
                        ChatMessageORM.chat_session_id == chat_session_id
                    )
                ).scalar_one()

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
            with get_db_session() as session:
                results = session.execute(
                    select(ChatMessageORM)
                    .where(ChatMessageORM.chat_session_id == chat_session_id)
                    .order_by(ChatMessageORM.created_at.desc())
                    .limit(limit)
                ).scalars().all()

                messages = [Message.model_validate(row) for row in results]

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
            offset = (page - 1) * page_size
            search_pattern = f"%{search_term}%"

            with get_db_session() as session:
                filter_clause = (
                    (ChatMessageORM.chat_session_id == chat_session_id)
                    & (ChatMessageORM.messages.like(search_pattern))
                )

                total_count = session.execute(
                    select(func.count()).select_from(ChatMessageORM).where(filter_clause)
                ).scalar_one()

                results = session.execute(
                    select(ChatMessageORM)
                    .where(filter_clause)
                    .order_by(ChatMessageORM.created_at.desc())
                    .limit(page_size)
                    .offset(offset)
                ).scalars().all()

                messages = [Message.model_validate(row) for row in results]

            log_debug(f"Found {len(messages)} messages matching '{search_term}' in chat session {chat_session_id}")
            return messages, total_count

        except Exception as e:
            log_error(f"Error searching messages in chat session {chat_session_id}: {e}")
            raise
