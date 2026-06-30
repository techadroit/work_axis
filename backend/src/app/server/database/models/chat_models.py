from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    """Model for creating a new chat"""
    user_id: str
    title: Optional[str] = None
    chat_session_id: Optional[str] = None


class ChatUpdate(BaseModel):
    """Model for updating a chat"""
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class Chat(BaseModel):
    """Model representing a chat"""
    chat_session_id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_archived: bool = False

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Model for creating a new message"""
    chat_session_id: str
    sender: str
    receiver: str
    messages: str
    mode: str = "none"
    message_id: Optional[str] = None
    utc_time: Optional[str] = None


class MessageUpdate(BaseModel):
    """Model for updating a message"""
    messages: str


class Message(BaseModel):
    """Model representing a message"""
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


class ChatWithMessageCount(Chat):
    """Chat model with message count"""
    message_count: int = 0


class ChatWithMessages(Chat):
    """Chat model with its messages"""
    messages: list[Message] = Field(default_factory=list)

