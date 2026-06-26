from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """Model for creating a new chat session"""
    user_id: str
    title: Optional[str] = None
    chat_session_id: Optional[str] = None


class ChatSessionUpdate(BaseModel):
    """Model for updating a chat session"""
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class ChatSession(BaseModel):
    """Model representing a chat session"""
    chat_session_id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_archived: bool = False

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Model for creating a new message (chat)"""
    chat_session_id: str
    sender: str
    receiver: str
    messages: str
    mode: str = "none"
    message_id: Optional[str] = None
    utc_time: Optional[str] = None
    content_type: Optional[str] = None
    message_type: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None


class MessageUpdate(BaseModel):
    """Model for updating a message"""
    messages: str


class Message(BaseModel):
    """Model representing a message (chat)"""
    message_id: str
    chat_session_id: str
    utc_time: str
    sender: str
    receiver: str
    messages: str
    mode: str
    created_at: datetime
    content_type: Optional[str] = "text"
    message_type: Optional[str] = "message"
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None

    class Config:
        from_attributes = True


class ChatSessionWithMessageCount(ChatSession):
    """Chat session model with message count"""
    message_count: int = 0


class ChatSessionWithMessages(ChatSession):
    """Chat session model with its messages"""
    messages: list[Message] = Field(default_factory=list)
