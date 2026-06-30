"""User models for database operations"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Model for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    full_name: Optional[str] = None
    user_id: Optional[str] = None  # Optional, will be generated if not provided


class UserUpdate(BaseModel):
    """Model for updating a user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    last_login: Optional[datetime] = None


class User(BaseModel):
    """Model representing a user"""
    user_id: str
    username: str
    email: str
    password_hash: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Model for user response (without sensitive data)"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str


class UserWithStats(UserResponse):
    """User model with additional statistics"""
    total_chat_sessions: int = 0
    total_messages: int = 0
    active_chat_sessions: int = 0

