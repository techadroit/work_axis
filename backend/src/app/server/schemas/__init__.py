"""
Schemas package for WorkAxis application.
Contains request and response Pydantic models for API operations.
"""

from src.app.server.schemas.chat_session_schemas import (
    # Request schemas
    ChatSessionCreateRequest,
    ChatSessionUpdateRequest,

    # Response schemas
    ChatSessionResponse,
    ChatSessionWithMessagesResponse,
    ChatSessionWithCountResponse,

    # Operation response schemas
    ChatSessionCreateResponse,
    ChatSessionListResponse,
    OperationResponse,
)

from src.app.server.schemas.chat_message_schemas import (
    # Message request schemas
    MessageCreateRequest,
    MessageUpdateRequest,
    MessageSearchRequest,

    # Message response schemas
    MessageResponse,
    MessageCreateResponse,
    MessageListResponse,
    MessageSearchResponse,
    MessageStatsResponse,
    MessageOperationResponse,
)

from src.app.server.schemas.user_schemas import (
    # User request schemas
    UserCreateRequest,
    UserUpdateRequest,
    UserLoginRequest,
    UserPasswordChangeRequest,
    AnonymousUserRequest,

    # User response schemas
    UserResponse,
    UserCreateResponse,
    UserLoginResponse,
    UserListResponse,
    UserWithStatsResponse,
    UserOperationResponse,
    AnonymousUserResponse,
)

__all__ = [
    # Chat session request schemas
    "ChatSessionCreateRequest",
    "ChatSessionUpdateRequest",

    # Chat session response schemas
    "ChatSessionResponse",
    "ChatSessionWithMessagesResponse",
    "ChatSessionWithCountResponse",

    # Chat session operation response schemas
    "ChatSessionCreateResponse",
    "ChatSessionListResponse",
    "OperationResponse",

    # Message request schemas
    "MessageCreateRequest",
    "MessageUpdateRequest",
    "MessageSearchRequest",

    # Message response schemas
    "MessageResponse",
    "MessageCreateResponse",
    "MessageListResponse",
    "MessageSearchResponse",
    "MessageStatsResponse",
    "MessageOperationResponse",

    # User request schemas
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserLoginRequest",
    "UserPasswordChangeRequest",
    "AnonymousUserRequest",

    # User response schemas
    "UserResponse",
    "UserCreateResponse",
    "UserLoginResponse",
    "UserListResponse",
    "UserWithStatsResponse",
    "UserOperationResponse",
    "AnonymousUserResponse",
]

