"""Request and Response schemas for Chat Message operations"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ========== Request Schemas ==========

class MessageCreateRequest(BaseModel):
    """Request schema for creating a new message"""
    chat_session_id: str = Field(..., description="ID of the chat session")
    sender: str = Field(..., description="Sender of the message (user/assistant)")
    receiver: str = Field(..., description="Receiver of the message")
    messages: str = Field(..., description="Message content")
    mode: str = Field(default="none", description="Message mode (document, websearch, agent, none)")
    message_id: str = Field(..., description="ID of the message")
    utc_time: str = Field(..., description="UTC time of the message")
    content_type: str = Field(default="text", description="Content type of the message (text, image, file)")
    message_type: str = Field(default="message", description="Type of the message (message, update_title)")
    file_name: Optional[str] = Field(None, description="Name of uploaded file (if any)")
    file_path: Optional[str] = Field(None, description="Path to uploaded file (if any)")
    mime_type: Optional[str] = Field(None, description="MIME type of uploaded file (if any)")


class MessageUpdateRequest(BaseModel):
    """Request schema for updating a message"""
    messages: str = Field(..., description="Updated message content")


class MessageSearchRequest(BaseModel):
    """Request schema for searching messages"""
    chat_session_id: str = Field(..., description="ID of the chat session")
    search_term: str = Field(..., min_length=1, description="Text to search for")
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of messages per page")


# ========== Response Schemas ==========

class MessageResponse(BaseModel):
    """Response schema for a single message"""
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


class MessageCreateResponse(BaseModel):
    """Response for message creation"""
    message_id: str
    chat_session_id: str
    message: str = "Message created successfully"


class MessageListResponse(BaseModel):
    """Response for listing messages with pagination"""
    messages: List[MessageResponse]
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_previous: bool


class MessageSearchResponse(BaseModel):
    """Response for message search with pagination"""
    messages: List[MessageResponse]
    search_term: str
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_previous: bool


class MessageStatsResponse(BaseModel):
    """Response for message statistics"""
    chat_session_id: str
    total_messages: int
    latest_message_time: Optional[datetime] = None


class MessageOperationResponse(BaseModel):
    """Generic message operation response"""
    success: bool
    message: str
    message_id: Optional[str] = None
    data: Optional[dict] = None
