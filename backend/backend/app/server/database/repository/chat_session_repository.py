import uuid
from typing import List, Optional

from backend.app.server.database.db_session import get_db_connection, TABLE_CHAT_SESSIONS, TABLE_CHAT_MESSAGES
from backend.app.server.database.models.chat_models import (
    Chat, ChatCreate, ChatUpdate
)
from backend.app.server.schemas import ChatSessionCreateResponse
from backend.app.utils.logger_util import log_info, log_error, log_debug


class ChatSessionRepository:
    """Repository for managing chat and chat_messages CRUD operations"""

    @staticmethod
    async def create_chat(chat_create: ChatCreate) -> ChatSessionCreateResponse:
        """
        Create a new chat session for a user.

        Args:
            chat_create: ChatCreate model containing user_id, optional title and chat_session_id

        Returns:
            The chat_session_id of the newly created chat
        """
        try:
            conn = get_db_connection()

            chat_session_id = chat_create.chat_session_id if chat_create.chat_session_id else str(uuid.uuid4())

            conn.execute(f"""
                INSERT INTO {TABLE_CHAT_SESSIONS} (chat_session_id, user_id, title, created_at, updated_at, is_archived)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE)
            """, [chat_session_id, chat_create.user_id, chat_create.title])

            conn.close()
            log_info(f"Created new chat: {chat_session_id} for user: {chat_create.user_id}")
            return ChatSessionCreateResponse(
                chat_session_id=chat_session_id,
                title=chat_create.title,
                message="Chat session created successfully"
            )

        except Exception as e:
            log_error(f"Error creating chat: {e}")
            raise

    @staticmethod
    def get_chat_by_id(chat_session_id: str) -> Optional[Chat]:
        """
        Get a chat by its ID.

        Args:
            chat_session_id: The ID of the chat to retrieve

        Returns:
            Chat model or None if not found
        """
        try:
            conn = get_db_connection()

            result = conn.execute(f"""
                SELECT chat_session_id, user_id, title, created_at, updated_at, is_archived
                FROM {TABLE_CHAT_SESSIONS}
                WHERE chat_session_id = ?
            """, [chat_session_id]).fetchone()

            conn.close()

            if result:
                return Chat(
                    chat_session_id=result[0],
                    user_id=result[1],
                    title=result[2],
                    created_at=result[3],
                    updated_at=result[4],
                    is_archived=result[5]
                )
            return None

        except Exception as e:
            log_error(f"Error getting chat by ID {chat_session_id}: {e}")
            raise

    @staticmethod
    def session_exist(chat_session_id: str) -> bool:
        """
        Get a chat by its ID.
        Args:
            chat_session_id: The ID of the chat to retrieve
        Returns:
            Chat model or None if not found
        """
        try:
            conn = get_db_connection()
            result = conn.execute(f"""
                SELECT COUNT(*) AS session_count
                FROM {TABLE_CHAT_SESSIONS}
                WHERE chat_session_id = ?;
            """,[chat_session_id]).fetchone()
            conn.close()
            if result[0] == 1:
                return True
            return False
        except Exception as e:
            log_error(f"Error getting chat by ID {chat_session_id}: {e}")
            raise

    @staticmethod
    def get_chats_by_user(user_id: str, include_archived: bool = False) -> List[Chat]:
        """
        Get all chats for a specific user.

        Args:
            user_id: The ID of the user
            include_archived: Whether to include archived chats

        Returns:
            List of Chat models
        """
        try:
            conn = get_db_connection()

            if include_archived:
                query = f"""
                    SELECT chat_session_id, user_id, title, created_at, updated_at, is_archived
                    FROM {TABLE_CHAT_SESSIONS}
                    WHERE user_id = ?
                    ORDER BY updated_at DESC
                """
            else:
                query = f"""
                    SELECT chat_session_id, user_id, title, created_at, updated_at, is_archived
                    FROM {TABLE_CHAT_SESSIONS}
                    WHERE user_id = ? AND is_archived = FALSE
                    ORDER BY updated_at DESC
                """

            results = conn.execute(query, [user_id]).fetchall()
            conn.close()

            chats = []
            for row in results:
                chats.append(Chat(
                    chat_session_id=row[0],
                    user_id=row[1],
                    title=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                    is_archived=row[5]
                ))

            log_debug(f"Retrieved {len(chats)} chats for user {user_id}")
            return chats

        except Exception as e:
            log_error(f"Error getting chats for user {user_id}: {e}")
            raise

    @staticmethod
    async def update_chat(chat_session_id: str, chat_update: ChatUpdate) -> bool:
        """
        Update a chat.

        Args:
            chat_session_id: The ID of the chat to update
            chat_update: ChatUpdate model with fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            # Build dynamic update query based on what fields are provided
            update_fields = []
            values = []

            if chat_update.title is not None:
                update_fields.append("title = ?")
                values.append(chat_update.title)

            if chat_update.is_archived is not None:
                update_fields.append("is_archived = ?")
                values.append(chat_update.is_archived)

            if not update_fields:
                log_debug(f"No fields to update for chat {chat_session_id}")
                return True

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(chat_session_id)

            query = f"UPDATE {TABLE_CHAT_SESSIONS} SET {', '.join(update_fields)} WHERE chat_session_id = ?"
            conn.execute(query, values)

            conn.close()
            log_info(f"Updated chat {chat_session_id}")
            return True

        except Exception as e:
            log_error(f"Error updating chat {chat_session_id}: {e}")
            return False

    @staticmethod
    def archive_chat(chat_session_id: str) -> bool:
        """
        Archive a chat (soft delete).

        Args:
            chat_session_id: The ID of the chat to archive

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            conn.execute(f"""
                UPDATE {TABLE_CHAT_SESSIONS}
                SET is_archived = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE chat_session_id = ?
            """, [chat_session_id])

            conn.close()
            log_info(f"Archived chat {chat_session_id}")
            return True

        except Exception as e:
            log_error(f"Error archiving chat {chat_session_id}: {e}")
            return False

    @staticmethod
    def unarchive_chat(chat_session_id: str) -> bool:
        """
        Unarchive a chat.

        Args:
            chat_session_id: The ID of the chat to unarchive

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            conn.execute(f"""
                UPDATE {TABLE_CHAT_SESSIONS}
                SET is_archived = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE chat_session_id = ?
            """, [chat_session_id])

            conn.close()
            log_info(f"Unarchived chat {chat_session_id}")
            return True

        except Exception as e:
            log_error(f"Error unarchiving chat {chat_session_id}: {e}")
            return False

    @staticmethod
    def delete_chat(chat_session_id: str) -> bool:
        """
        Permanently delete a chat and all its messages.

        Args:
            chat_session_id: The ID of the chat to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            # Delete all messages first (due to foreign key constraint)
            conn.execute(f"DELETE FROM {TABLE_CHAT_MESSAGES} WHERE chat_session_id = ?", [chat_session_id])

            # Delete the chat
            conn.execute(f"DELETE FROM {TABLE_CHAT_SESSIONS} WHERE chat_session_id = ?", [chat_session_id])

            conn.close()
            log_info(f"Permanently deleted chat {chat_session_id} and its messages")
            return True

        except Exception as e:
            log_error(f"Error deleting chat {chat_session_id}: {e}")
            return False


