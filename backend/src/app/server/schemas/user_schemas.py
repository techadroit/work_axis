"""Request and Response schemas for User operations"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ========== Request Schemas ==========

class UserCreateRequest(BaseModel):
    """Request schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (will be hashed)")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserUpdateRequest(BaseModel):
    """Request schema for updating a user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="New username")
    email: Optional[EmailStr] = Field(None, description="New email address")
    password: Optional[str] = Field(None, min_length=8, description="New password (will be hashed)")
    full_name: Optional[str] = Field(None, description="New full name")
    is_active: Optional[bool] = Field(None, description="Active status")


class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User's password")
    anonymous_user_id: Optional[str] = Field(None, description="Anonymous user ID to migrate data from")


class UserPasswordChangeRequest(BaseModel):
    """Request schema for changing password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class AnonymousUserRequest(BaseModel):
    """Request schema for creating an anonymous user"""
    device_id: Optional[str] = Field(None, description="Optional device identifier")


# ========== Response Schemas ==========

class UserResponse(BaseModel):
    """Response schema for user (excludes sensitive data)"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreateResponse(BaseModel):
    """Response for user creation"""
    user_id: str
    username: str
    email: str
    message: str = "User created successfully"


class UserLoginResponse(BaseModel):
    """Response for user login"""
    user_id: str
    username: str
    email: str
    token: Optional[str] = None  # For JWT token if implemented
    message: str = "Login successful"
    data_migrated: bool = False  # Indicates if anonymous data was migrated


class AnonymousUserResponse(BaseModel):
    """Response for anonymous user creation"""
    user_id: str
    is_anonymous: bool = True
    message: str = "Anonymous user created successfully"


class UserListResponse(BaseModel):
    """Response for listing users"""
    users: List[UserResponse]
    count: int


class UserWithStatsResponse(UserResponse):
    """Response with user statistics"""
    total_chat_sessions: int = 0
    total_messages: int = 0
    active_chat_sessions: int = 0


# ========== Operation Result Schemas ==========

class UserOperationResponse(BaseModel):
    """Generic user operation response"""
    success: bool
    message: str
    user_id: Optional[str] = None
    data: Optional[dict] = None

