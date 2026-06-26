"""Request and Response schemas for Chat Session operations"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ========== Request Schemas ==========

class ChatSessionCreateRequest(BaseModel):
    """Request schema for creating a new chat session"""
    user_id: str = Field(..., description="ID of the user creating the chat session")
    title: Optional[str] = Field(None, description="Optional title for the chat session")


class ChatSessionUpdateRequest(BaseModel):
    """Request schema for updating a chat session"""
    title: Optional[str] = Field(None, description="New title for the chat session")
    is_archived: Optional[bool] = Field(None, description="Archive status")


class MessageCreateRequest(BaseModel):
    """Request schema for creating a message"""
    chat_session_id: str = Field(..., description="ID of the chat session")
    sender: str = Field(..., description="Sender of the message")
    receiver: str = Field(..., description="Receiver of the message")
    messages: str = Field(..., description="Message content")
    mode: str = Field(default="none", description="Message mode (document, websearch, agent, none)")
    utc_time: str = Field(..., description="UTC time of the message creation")


# ========== Response Schemas ==========

class ChatSessionResponse(BaseModel):
    """Response schema for chat session"""
    chat_session_id: str
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_archived: bool

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Response schema for message"""
    message_id: str
    chat_session_id: str
    utc_time: str
    sender: str
    receiver: str
    messages: str
    mode: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessagesResponse(ChatSessionResponse):
    """Response schema for chat session with its messages"""
    messages: List[MessageResponse] = Field(default_factory=list)


class ChatSessionWithCountResponse(ChatSessionResponse):
    """Response schema for chat session with message count"""
    message_count: int = 0


# ========== Operation Result Schemas ==========

class ChatSessionCreateResponse(BaseModel):
    """Response for chat session creation"""
    chat_session_id: str
    title: str
    message: str = "Chat session created successfully"


class MessageCreateResponse(BaseModel):
    """Response for message creation"""
    message_id: str
    message: str = "Message created successfully"


class ChatSessionListResponse(BaseModel):
    """Response for listing chat sessions"""
    chat_sessions: List[ChatSessionResponse]
    count: int


class MessageListResponse(BaseModel):
    """Response for listing messages"""
    messages: List[MessageResponse]
    count: int


class OperationResponse(BaseModel):
    """Generic operation response"""
    success: bool
    message: str
    data: Optional[dict] = None
