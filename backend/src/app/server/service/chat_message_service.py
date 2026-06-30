"""Chat message service layer for business logic and operations"""
import uuid
from typing import Optional, List

from starlette.exceptions import HTTPException

from src.app.server.database.chat_message_repository import ChatMessageRepository
from src.app.server.database.models.chat_session_models import MessageCreate, MessageUpdate
from src.app.server.database.repository.chat_session_repository import ChatSessionRepository
from src.app.server.database.user_repository import UserRepository
from src.app.server.schemas.chat_message_schemas import (
    MessageCreateRequest, MessageUpdateRequest,
    MessageResponse, MessageCreateResponse,
    MessageListResponse, MessageOperationResponse,
    MessageStatsResponse, MessageSearchResponse
)
from src.app.utils.logger_util import log_info, log_error, log_debug
from core.utils.time_util import get_current_timestamp_ns_datetime


class ChatMessageService:
    """
    Service layer for chat message operations.
    Acts as an intermediate layer between routes and repository.
    Handles business logic, validation, and schema/model conversion.
    """

    def __init__(self):
        self.repository = ChatMessageRepository()
        self.user_repository = UserRepository()
        self.chat_session_repository = ChatSessionRepository()

    def save_message(self, request: MessageCreateRequest) -> MessageCreateResponse:
        """
        Create a new message in a chat session.

        Args:
            request: MessageCreateRequest schema from routes

        Returns:
            MessageCreateResponse with the message_id

        Raises:
            ValueError: If validation fails
            Exception: If message creation fails
        """
        try:
            log_info(f"Service: Creating message in chat session: {request}")

            # Validate required fields
            if not request.chat_session_id or not request.sender:
                raise ValueError("chat_session_id and sender are required")

            # Convert request schema to repository model
            message_create = MessageCreate(
                chat_session_id=request.chat_session_id,
                sender=request.sender,
                receiver=request.receiver,
                messages=request.messages,
                mode=request.mode,
                message_id=request.message_id,  # Let repository generate it
                utc_time=request.utc_time,  # Let repository generate it,
                content_type=request.content_type,
                message_type=request.message_type,
                file_name=request.file_name,
                file_path=request.file_path,
                mime_type=request.mime_type
            )

            # Call repository to create message
            self.repository.create_message(message_create)

            # log_info(f"Service: Successfully created message {request.message_id}")

            # Return response schema
            return MessageCreateResponse(
                message_id=request.message_id,
                chat_session_id=request.chat_session_id,
                message="Message created successfully"
            )

        except ValueError as e:
            log_error(f"Service: Validation error creating message: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error creating message: {e}")
            raise

    def get_message_by_id(self, message_id: str) -> Optional[MessageResponse]:
        """
        Get a message by its ID.

        Args:
            message_id: The ID of the message to retrieve

        Returns:
            MessageResponse or None if not found
        """
        try:
            log_debug(f"Service: Fetching message {message_id}")

            if not message_id:
                raise ValueError("message_id is required")

            # Call repository to get message
            message = self.repository.get_message_by_id(message_id)

            if message:
                log_debug(f"Service: Found message {message_id}")

                # Convert model to response schema
                return MessageResponse(
                    message_id=message.message_id,
                    chat_session_id=message.chat_session_id,
                    utc_time=message.utc_time,
                    sender=message.sender,
                    receiver=message.receiver,
                    messages=message.messages,
                    mode=message.mode,
                    created_at=message.created_at
                )
            else:
                log_debug(f"Service: Message {message_id} not found")
                return None

        except Exception as e:
            log_error(f"Service: Error fetching message {message_id}: {e}")
            raise

    def get_messages_by_chat_session(
            self,
            chat_session_id: str,
            page: int = 1,
            page_size: int = 20
    ) -> MessageListResponse:
        """
        Get messages for a chat session with pagination.

        Args:
            chat_session_id: The ID of the chat session
            page: Page number (1-based)
            page_size: Number of messages per page (default: 20)

        Returns:
            MessageListResponse with paginated messages

        Raises:
            ValueError: If validation fails
        """
        try:
            if not chat_session_id:
                raise HTTPException(status_code=422,detail="Invalid session id")

            if page < 0:
                raise HTTPException(status_code=422, detail=f"Invalid page number {page}.")

            # Verify chat session exists
            chat_session = self.chat_session_repository.get_chat_by_id(chat_session_id)
            if not chat_session:
                raise ValueError(f"Chat session {chat_session_id} not found")

            # Call repository to get messages with pagination
            messages, total_count = self.repository.get_messages_by_chat_session(
                chat_session_id=chat_session_id,
                page=page,
                page_size=page_size
            )

            # Convert models to response schemas
            message_responses = [
                MessageResponse(
                    message_id=msg.message_id,
                    chat_session_id=msg.chat_session_id,
                    utc_time=msg.utc_time,
                    sender=msg.sender,
                    receiver=msg.receiver,
                    messages=msg.messages,
                    mode=msg.mode,
                    created_at=msg.created_at,
                    message_type=msg.message_type,
                    content_type=msg.content_type,
                    file_name=msg.file_name,
                    file_path=msg.file_path,
                    mime_type=msg.mime_type
                )
                for msg in messages
            ]

            # Calculate pagination info
            total_pages = (total_count + page_size) // page_size
            has_next = page < total_pages
            has_previous = page > 1

            log_info(
                f"Service: Found {len(message_responses)} messages for chat session {chat_session_id} (page {page}/{total_pages})")

            return MessageListResponse(
                messages=message_responses,
                page=page,
                page_size=page_size,
                total_count=total_count,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )

        except ValueError as e:
            log_error(f"Service: Validation error fetching messages: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error fetching messages for chat session {chat_session_id}: {e}")
            raise

    def get_all_messages_by_chat_session(self, chat_session_id: str) -> List[MessageResponse]:
        """
        Get all messages for a chat session without pagination.

        Args:
            chat_session_id: The ID of the chat session

        Returns:
            List of MessageResponse

        Raises:
            ValueError: If validation fails
        """
        try:
            log_debug(f"Service: Fetching all messages for chat session {chat_session_id}")

            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists
            chat_session = self.chat_session_repository.get_chat_by_id(chat_session_id)
            if not chat_session:
                raise ValueError(f"Chat session {chat_session_id} not found")

            # Call repository to get all messages
            messages = self.repository.get_all_messages_by_chat_session(chat_session_id)

            # Convert models to response schemas
            message_responses = [
                MessageResponse(
                    message_id=msg.message_id,
                    chat_session_id=msg.chat_session_id,
                    utc_time=msg.utc_time,
                    sender=msg.sender,
                    receiver=msg.receiver,
                    messages=msg.messages,
                    mode=msg.mode,
                    created_at=msg.created_at
                )
                for msg in messages
            ]

            log_info(f"Service: Found {len(message_responses)} total messages for chat session {chat_session_id}")

            return message_responses

        except ValueError as e:
            log_error(f"Service: Validation error fetching all messages: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error fetching all messages for chat session {chat_session_id}: {e}")
            raise

    def update_message(self, message_id: str, request: MessageUpdateRequest) -> MessageOperationResponse:
        """
        Update a message's content.

        Args:
            message_id: The ID of the message to update
            request: MessageUpdateRequest schema with new content

        Returns:
            MessageOperationResponse with success status and message
        """
        try:
            log_info(f"Service: Updating message {message_id}")

            if not message_id:
                raise ValueError("message_id is required")

            if not request.messages:
                raise ValueError("messages content is required")

            # Verify message exists before updating
            existing_message = self.repository.get_message_by_id(message_id)
            if not existing_message:
                log_error(f"Service: Message {message_id} not found for update")
                return MessageOperationResponse(
                    success=False,
                    message=f"Message {message_id} not found",
                    message_id=message_id
                )

            # Convert request schema to repository model
            message_update = MessageUpdate(messages=request.messages)

            # Call repository to update message
            success = self.repository.update_message(message_id, message_update)

            if success:
                log_info(f"Service: Successfully updated message {message_id}")
                return MessageOperationResponse(
                    success=True,
                    message="Message updated successfully",
                    message_id=message_id
                )
            else:
                log_error(f"Service: Failed to update message {message_id}")
                return MessageOperationResponse(
                    success=False,
                    message="Failed to update message",
                    message_id=message_id
                )

        except ValueError as e:
            log_error(f"Service: Validation error updating message {message_id}: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error updating message {message_id}: {e}")
            raise

    def delete_message(self, message_id: str) -> MessageOperationResponse:
        """
        Permanently delete a message.

        Args:
            message_id: The ID of the message to delete

        Returns:
            MessageOperationResponse with success status and message
        """
        try:
            log_info(f"Service: Deleting message {message_id}")

            if not message_id:
                raise ValueError("message_id is required")

            # Verify message exists before deleting
            existing_message = self.repository.get_message_by_id(message_id)
            if not existing_message:
                log_error(f"Service: Message {message_id} not found for deletion")
                return MessageOperationResponse(
                    success=False,
                    message=f"Message {message_id} not found",
                    message_id=message_id
                )

            # Call repository to delete message
            success = self.repository.delete_message(message_id)

            if success:
                log_info(f"Service: Successfully deleted message {message_id}")
                return MessageOperationResponse(
                    success=True,
                    message="Message deleted successfully",
                    message_id=message_id
                )
            else:
                log_error(f"Service: Failed to delete message {message_id}")
                return MessageOperationResponse(
                    success=False,
                    message="Failed to delete message",
                    message_id=message_id
                )

        except ValueError as e:
            log_error(f"Service: Validation error deleting message {message_id}: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error deleting message {message_id}: {e}")
            raise

    def delete_messages_by_chat_session(self, chat_session_id: str) -> MessageOperationResponse:
        """
        Delete all messages in a chat session.

        Args:
            chat_session_id: The ID of the chat session

        Returns:
            MessageOperationResponse with success status and message
        """
        try:
            log_info(f"Service: Deleting all messages for chat session {chat_session_id}")

            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists
            chat_session = self.chat_session_repository.get_chat_by_id(chat_session_id)
            if not chat_session:
                return MessageOperationResponse(
                    success=False,
                    message=f"Chat session {chat_session_id} not found"
                )

            # Call repository to delete all messages
            success = self.repository.delete_messages_by_chat_session(chat_session_id)

            if success:
                log_info(f"Service: Successfully deleted all messages for chat session {chat_session_id}")
                return MessageOperationResponse(
                    success=True,
                    message="All messages deleted successfully"
                )
            else:
                log_error(f"Service: Failed to delete messages for chat session {chat_session_id}")
                return MessageOperationResponse(
                    success=False,
                    message="Failed to delete messages"
                )

        except ValueError as e:
            log_error(f"Service: Validation error deleting messages: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error deleting messages for chat session {chat_session_id}: {e}")
            raise

    def get_message_stats(self, chat_session_id: str) -> MessageStatsResponse:
        """
        Get statistics for messages in a chat session.

        Args:
            chat_session_id: The ID of the chat session

        Returns:
            MessageStatsResponse with statistics

        Raises:
            ValueError: If validation fails
        """
        try:
            log_debug(f"Service: Getting message stats for chat session {chat_session_id}")

            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            # Verify chat session exists
            chat_session = self.chat_session_repository.get_chat_by_id(chat_session_id)
            if not chat_session:
                raise ValueError(f"Chat session {chat_session_id} not found")

            # Get message count
            total_messages = self.repository.get_message_count_by_chat_session(chat_session_id)

            # Get latest message for timestamp
            latest_message_time = None
            if total_messages > 0:
                latest_messages = self.repository.get_latest_messages(chat_session_id, limit=1)
                if latest_messages:
                    latest_message_time = latest_messages[0].created_at

            return MessageStatsResponse(
                chat_session_id=chat_session_id,
                total_messages=total_messages,
                latest_message_time=latest_message_time
            )

        except ValueError as e:
            log_error(f"Service: Validation error getting message stats: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error getting message stats for chat session {chat_session_id}: {e}")
            raise

    def search_messages(
            self,
            chat_session_id: str,
            search_term: str,
            page: int = 1,
            page_size: int = 20
    ) -> MessageSearchResponse:
        """
        Search messages in a chat session by content.

        Args:
            chat_session_id: The ID of the chat session
            search_term: Text to search for in message content
            page: Page number (1-based)
            page_size: Number of messages per page (default: 20)

        Returns:
            MessageSearchResponse with search results

        Raises:
            ValueError: If validation fails
        """
        try:
            log_debug(f"Service: Searching messages in chat session {chat_session_id} for '{search_term}'")

            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            if not search_term or len(search_term.strip()) == 0:
                raise ValueError("search_term is required and cannot be empty")

            if page < 1:
                raise ValueError("page must be >= 1")

            if page_size < 1 or page_size > 100:
                raise ValueError("page_size must be between 1 and 100")

            # Verify chat session exists
            chat_session = self.chat_session_repository.get_chat_by_id(chat_session_id)
            if not chat_session:
                raise ValueError(f"Chat session {chat_session_id} not found")

            # Call repository to search messages
            messages, total_count = self.repository.search_messages(
                chat_session_id=chat_session_id,
                search_term=search_term,
                page=page,
                page_size=page_size
            )

            # Convert models to response schemas
            message_responses = [
                MessageResponse(
                    message_id=msg.message_id,
                    chat_session_id=msg.chat_session_id,
                    utc_time=msg.utc_time,
                    sender=msg.sender,
                    receiver=msg.receiver,
                    messages=msg.messages,
                    mode=msg.mode,
                    created_at=msg.created_at
                )
                for msg in messages
            ]

            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1

            log_info(
                f"Service: Found {total_count} messages matching '{search_term}' in chat session {chat_session_id}")

            return MessageSearchResponse(
                messages=message_responses,
                search_term=search_term,
                page=page,
                page_size=page_size,
                total_count=total_count,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )

        except ValueError as e:
            log_error(f"Service: Validation error searching messages: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error searching messages in chat session {chat_session_id}: {e}")
            raise

    def get_latest_messages(
            self,
            chat_session_id: str,
            limit: int = 10
    ) -> List[MessageResponse]:
        """
        Get the latest N messages from a chat session.

        Args:
            chat_session_id: The ID of the chat session
            limit: Number of latest messages to retrieve

        Returns:
            List of MessageResponse (latest first)

        Raises:
            ValueError: If validation fails
        """
        try:
            log_debug(f"Service: Fetching latest {limit} messages for chat session {chat_session_id}")

            if not chat_session_id:
                raise ValueError("chat_session_id is required")

            if limit < 1 or limit > 100:
                raise ValueError("limit must be between 1 and 100")

            # Verify chat session exists
            chat_session = self.chat_session_repository.get_chat_by_id(chat_session_id)
            if not chat_session:
                raise ValueError(f"Chat session {chat_session_id} not found")

            # Call repository to get latest messages
            messages = self.repository.get_latest_messages(chat_session_id, limit=limit)

            # Convert models to response schemas
            message_responses = [
                MessageResponse(
                    message_id=msg.message_id,
                    chat_session_id=msg.chat_session_id,
                    utc_time=msg.utc_time,
                    sender=msg.sender,
                    receiver=msg.receiver,
                    messages=msg.messages,
                    mode=msg.mode,
                    created_at=msg.created_at
                )
                for msg in messages
            ]

            log_info(f"Service: Retrieved {len(message_responses)} latest messages for chat session {chat_session_id}")

            return message_responses

        except ValueError as e:
            log_error(f"Service: Validation error fetching latest messages: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error fetching latest messages for chat session {chat_session_id}: {e}")
            raise

    def generate_chat_message_id(self, prefix="CHAT") -> str:
        """Generate a chat message ID with prefix and timestamp"""
        timestamp = get_current_timestamp_ns_datetime()
        unique_part = str(uuid.uuid4())
        return f"{prefix}_{timestamp}_{unique_part}"


_chat_message_service = ChatMessageService()


def get_chat_message_service() -> ChatMessageService:
    """Dependency injection for ChatMessageService"""
    return _chat_message_service
