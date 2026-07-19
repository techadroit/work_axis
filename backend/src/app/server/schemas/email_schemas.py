"""Pydantic schemas for email integration (Gmail OAuth + file import)"""
from typing import Optional

from pydantic import BaseModel, Field


class EmailProviderCredentialsCreate(BaseModel):
    """Schema for saving a provider's OAuth Client ID/Secret (e.g. Gmail)"""
    provider: str = Field(..., description="Email provider name, e.g. 'gmail'")
    client_id: str = Field(..., description="OAuth Client ID from the provider's developer console")
    client_secret: str = Field(..., description="OAuth Client Secret (stored encrypted)")
    redirect_uri: str = Field(..., description="Exact redirect URI registered with the provider")


class EmailProviderCredentials(BaseModel):
    """Schema for returning provider credential configuration status (never includes the secret)"""
    id: str
    provider: str
    client_id: str
    redirect_uri: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class EmailAccount(BaseModel):
    """Schema for a connected mailbox / file-import batch (never includes tokens)"""
    id: str
    user_id: str
    provider: str
    email_address: str
    display_name: Optional[str] = None
    scopes: Optional[str] = None
    status: str
    last_sync_status: Optional[str] = None
    last_sync_error: Optional[str] = None
    last_synced_at: Optional[str] = None
    total_messages_synced: int = 0
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class EmailAccountResponse(BaseModel):
    """Response schema for email account operations"""
    success: bool
    message: str
    data: Optional[EmailAccount] = None


class EmailSyncStatusResponse(BaseModel):
    """Response schema for polling sync progress"""
    account_id: str
    status: str
    last_synced_at: Optional[str] = None
    total_messages_synced: int = 0
    last_sync_error: Optional[str] = None
