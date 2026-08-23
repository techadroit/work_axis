import uuid
from typing import List, Optional

from sqlalchemy import select, func

from src.app.server.database.db_session import get_db_session
from src.app.server.database.orm_models import ChatSessionORM, ChatMessageORM
from src.app.server.database.models.chat_models import (
    Chat, ChatCreate, ChatUpdate
)
from src.app.server.schemas import ChatSessionCreateResponse
from src.app.utils.logger_util import log_info, log_error, log_debug


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
            chat_session_id = chat_create.chat_session_id if chat_create.chat_session_id else str(uuid.uuid4())

            with get_db_session() as session:
                chat_session = ChatSessionORM(
                    chat_session_id=chat_session_id,
                    user_id=chat_create.user_id,
                    title=chat_create.title,
                )
                session.add(chat_session)

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
            with get_db_session() as session:
                chat_session = session.get(ChatSessionORM, chat_session_id)
                return Chat.model_validate(chat_session) if chat_session else None

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
            with get_db_session() as session:
                count = session.execute(
                    select(func.count()).select_from(ChatSessionORM).where(
                        ChatSessionORM.chat_session_id == chat_session_id
                    )
                ).scalar_one()
                return count == 1
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
            with get_db_session() as session:
                query = select(ChatSessionORM).where(ChatSessionORM.user_id == user_id)
                if not include_archived:
                    query = query.where(ChatSessionORM.is_archived.is_(False))
                query = query.order_by(ChatSessionORM.updated_at.desc())

                results = session.execute(query).scalars().all()
                chats = [Chat.model_validate(row) for row in results]

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
            update_data = chat_update.model_dump(exclude_unset=True, exclude_none=True)
            if not update_data:
                log_debug(f"No fields to update for chat {chat_session_id}")
                return True

            with get_db_session() as session:
                chat_session = session.get(ChatSessionORM, chat_session_id)
                if chat_session is None:
                    log_debug(f"Chat {chat_session_id} not found for update")
                    return False

                for field, value in update_data.items():
                    setattr(chat_session, field, value)
                chat_session.updated_at = func.current_timestamp()

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
            with get_db_session() as session:
                chat_session = session.get(ChatSessionORM, chat_session_id)
                if chat_session is None:
                    return False
                chat_session.is_archived = True
                chat_session.updated_at = func.current_timestamp()

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
            with get_db_session() as session:
                chat_session = session.get(ChatSessionORM, chat_session_id)
                if chat_session is None:
                    return False
                chat_session.is_archived = False
                chat_session.updated_at = func.current_timestamp()

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
            with get_db_session() as session:
                # Delete all messages first (due to foreign key constraint)
                session.execute(
                    ChatMessageORM.__table__.delete().where(
                        ChatMessageORM.chat_session_id == chat_session_id
                    )
                )

                # Delete the chat
                session.execute(
                    ChatSessionORM.__table__.delete().where(
                        ChatSessionORM.chat_session_id == chat_session_id
                    )
                )

            log_info(f"Permanently deleted chat {chat_session_id} and its messages")
            return True

        except Exception as e:
            log_error(f"Error deleting chat {chat_session_id}: {e}")
            return False
