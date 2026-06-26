from typing import Optional

from backend.app.server.database.repository.chat_session_repository import ChatSessionRepository
from backend.app.server.database.models.chat_models import ChatCreate, ChatUpdate
from backend.app.server.database.user_repository import UserRepository
from backend.app.server.schemas.chat_session_schemas import (
    ChatSessionCreateRequest, ChatSessionUpdateRequest,
    ChatSessionResponse, ChatSessionListResponse,
    ChatSessionCreateResponse, OperationResponse
)
from backend.app.utils.logger_util import log_info, log_error, log_debug


class ChatSessionService:
    """
    Service layer for chat session operations.
    Acts as an intermediate layer between routes and repository.
    Handles business logic and validation.
    """

    def __init__(self):
        self.repository = ChatSessionRepository()
        self.user_repository = UserRepository()

    async def create_chat_session(self, request: ChatSessionCreateRequest) -> ChatSessionCreateResponse:
        """
        Create a new chat session for a user.

        Args:
            request: ChatSessionCreateRequest schema from routes

        Returns:
            ChatSessionCreateResponse with the chat_session_id

        Raises:
            Exception: If chat session creation fails
        """
        try:
            log_info(f"Service: Creating chat session for user: {request.user_id}")

            # Add any business logic validation here if needed
            if not request.user_id:
                raise ValueError("user_id is required to create a chat session")

            user_exist = self.user_repository.check_user_exists(request.user_id)

            if not user_exist:
                raise ValueError(f"User {request.user_id} does not exist")

            # Convert request schema to repository model
            chat_create = ChatCreate(
                user_id=request.user_id,
                title=request.title,
                chat_session_id=None  # Let repository generate it
            )

            # Call repository to create chat session
            response = await self.repository.create_chat(chat_create)

            log_info(f"Service: Successfully created chat session {response}")

            # Return response schema
            return response

        except Exception as e:
            log_error(f"Service: Error creating chat session: {e}")
            raise

    def session_exist(self,chat_session_id:str) -> bool:
        return self.repository.session_exist(chat_session_id)

    def get_chat_session_by_id(self, chat_session_id: str) -> Optional[ChatSessionResponse]:
        """
        Get a chat session by its ID.

        Args:
            chat_session_id: The ID of the chat session to retrieve

        Returns:
            ChatSessionResponse or None if not found

        Raises:
            Exception: If retrieval fails
        """
        try:
            log_debug(f"Service: Fetching chat session {chat_session_id}")

            # Add any business logic validation here if needed
            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Call repository to get chat session
            chat_session = self.repository.get_chat_by_id(chat_session_id)

            if chat_session:
                log_debug(f"Service: Found chat session {chat_session_id}")

                # Convert model to response schema
                return ChatSessionResponse(
                    chat_session_id=chat_session.chat_session_id,
                    user_id=chat_session.user_id,
                    title=chat_session.title,
                    created_at=chat_session.created_at,
                    updated_at=chat_session.updated_at,
                    is_archived=chat_session.is_archived
                )
            else:
                log_debug(f"Service: Chat session {chat_session_id} not found")
                return None

        except Exception as e:
            log_error(f"Service: Error fetching chat session {chat_session_id}: {e}")
            raise

    def get_chat_sessions_by_user(self, user_id: str, include_archived: bool = False) -> ChatSessionListResponse:
        """
        Get all chat sessions for a specific user.

        Args:
            user_id: The ID of the user
            include_archived: Whether to include archived chat sessions

        Returns:
            ChatSessionListResponse with list of chat sessions and count

        Raises:
            Exception: If retrieval fails
        """
        try:
            log_debug(f"Service: Fetching chat sessions for user {user_id} (include_archived={include_archived})")

            # Add any business logic validation here if needed
            if not user_id:
                raise ValueError("user_id is required")

            # Call repository to get chat sessions
            chat_sessions = self.repository.get_chats_by_user(user_id, include_archived)

            # Convert models to response schemas
            chat_session_responses = [
                ChatSessionResponse(
                    chat_session_id=chat.chat_session_id,
                    user_id=chat.user_id,
                    title=chat.title,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at,
                    is_archived=chat.is_archived
                )
                for chat in chat_sessions
            ]

            log_info(f"Service: Found {len(chat_session_responses)} chat sessions for user {user_id}")

            return ChatSessionListResponse(
                chat_sessions=chat_session_responses,
                count=len(chat_session_responses)
            )

        except Exception as e:
            log_error(f"Service: Error fetching chat sessions for user {user_id}: {e}")
            raise

    async def update_chat_session(self, chat_session_id: str, request: ChatSessionUpdateRequest) -> OperationResponse:
        """
        Update a chat session.

        Args:
            chat_session_id: The ID of the chat session to update
            request: ChatSessionUpdateRequest schema with fields to update

        Returns:
            OperationResponse with success status and message

        Raises:
            Exception: If update fails
        """
        try:
            log_info(f"Service: Updating chat session {chat_session_id}")

            # Add any business logic validation here if needed
            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists before updating
            existing_session = self.repository.get_chat_by_id(chat_session_id)
            if not existing_session:
                log_error(f"Service: Chat session {chat_session_id} not found for update")
                return OperationResponse(
                    success=False,
                    message=f"Chat session {chat_session_id} not found"
                )

            # Convert request schema to repository model
            chat_update = ChatUpdate(
                title=request.title,
                is_archived=request.is_archived
            )

            # Call repository to update chat session
            success = await self.repository.update_chat(chat_session_id, chat_update)

            if success:
                log_info(f"Service: Successfully updated chat session {chat_session_id}")
                return OperationResponse(
                    success=True,
                    message="Chat session updated successfully"
                )
            else:
                log_error(f"Service: Failed to update chat session {chat_session_id}")
                return OperationResponse(
                    success=False,
                    message="Failed to update chat session"
                )

        except Exception as e:
            log_error(f"Service: Error updating chat session {chat_session_id}: {e}")
            raise

    def archive_chat_session(self, chat_session_id: str) -> OperationResponse:
        """
        Archive a chat session (soft delete).

        Args:
            chat_session_id: The ID of the chat session to archive

        Returns:
            OperationResponse with success status and message

        Raises:
            Exception: If archiving fails
        """
        try:
            log_info(f"Service: Archiving chat session {chat_session_id}")

            # Add any business logic validation here if needed
            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists before archiving
            existing_session = self.repository.get_chat_by_id(chat_session_id)
            if not existing_session:
                log_error(f"Service: Chat session {chat_session_id} not found for archiving")
                return OperationResponse(
                    success=False,
                    message=f"Chat session {chat_session_id} not found"
                )

            # Call repository to archive chat session
            success = self.repository.archive_chat(chat_session_id)

            if success:
                log_info(f"Service: Successfully archived chat session {chat_session_id}")
                return OperationResponse(
                    success=True,
                    message="Chat session archived successfully"
                )
            else:
                log_error(f"Service: Failed to archive chat session {chat_session_id}")
                return OperationResponse(
                    success=False,
                    message="Failed to archive chat session"
                )

        except Exception as e:
            log_error(f"Service: Error archiving chat session {chat_session_id}: {e}")
            raise

    def unarchive_chat_session(self, chat_session_id: str) -> OperationResponse:
        """
        Unarchive a chat session.

        Args:
            chat_session_id: The ID of the chat session to unarchive

        Returns:
            OperationResponse with success status and message

        Raises:
            Exception: If unarchiving fails
        """
        try:
            log_info(f"Service: Unarchiving chat session {chat_session_id}")

            # Add any business logic validation here if needed
            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists before unarchiving
            existing_session = self.repository.get_chat_by_id(chat_session_id)
            if not existing_session:
                log_error(f"Service: Chat session {chat_session_id} not found for unarchiving")
                return OperationResponse(
                    success=False,
                    message=f"Chat session {chat_session_id} not found"
                )

            # Call repository to unarchive chat session
            success = self.repository.unarchive_chat(chat_session_id)

            if success:
                log_info(f"Service: Successfully unarchived chat session {chat_session_id}")
                return OperationResponse(
                    success=True,
                    message="Chat session unarchived successfully"
                )
            else:
                log_error(f"Service: Failed to unarchive chat session {chat_session_id}")
                return OperationResponse(
                    success=False,
                    message="Failed to unarchive chat session"
                )

        except Exception as e:
            log_error(f"Service: Error unarchiving chat session {chat_session_id}: {e}")
            raise

    def delete_chat_session(self, chat_session_id: str) -> OperationResponse:
        """
        Permanently delete a chat session and all its messages.

        Args:
            chat_session_id: The ID of the chat session to delete

        Returns:
            OperationResponse with success status and message

        Raises:
            Exception: If deletion fails
        """
        try:
            log_info(f"Service: Deleting chat session {chat_session_id}")

            # Add any business logic validation here if needed
            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists before deleting
            existing_session = self.repository.get_chat_by_id(chat_session_id)
            if not existing_session:
                log_error(f"Service: Chat session {chat_session_id} not found for deletion")
                return OperationResponse(
                    success=False,
                    message=f"Chat session {chat_session_id} not found"
                )

            # Additional business logic: maybe check if user has permission to delete
            # or log the deletion for audit purposes

            # Call repository to delete chat session
            success = self.repository.delete_chat(chat_session_id)

            if success:
                log_info(f"Service: Successfully deleted chat session {chat_session_id}")
                return OperationResponse(
                    success=True,
                    message="Chat session deleted successfully"
                )
            else:
                log_error(f"Service: Failed to delete chat session {chat_session_id}")
                return OperationResponse(
                    success=False,
                    message="Failed to delete chat session"
                )

        except Exception as e:
            log_error(f"Service: Error deleting chat session {chat_session_id}: {e}")
            raise

_chat_session_service = ChatSessionService()

def provide_chat_session_service() -> ChatSessionService:
    return _chat_session_service

