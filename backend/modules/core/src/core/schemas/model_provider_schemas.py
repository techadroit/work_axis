"""Pydantic schemas for model provider configuration"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ModelProviderBase(BaseModel):
    """Base schema for model provider"""
    provider_name: str = Field(..., description="Name of the model provider (OpenAI, Anthropic, Google, Azure, AWS, Ollama)")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Base URL for the API endpoint")
    api_version: Optional[str] = Field(None, description="API version (Azure specific)")
    deployment_name: Optional[str] = Field(None, description="Deployment name (Azure specific)")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID (AWS specific)")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key (AWS specific)")
    region: Optional[str] = Field(None, description="AWS region (AWS specific)")
    model_provider: Optional[str] = Field(None, description="Model provider configuration (AWS specific)")
    config_json: Optional[str] = Field(None, description="Additional configuration as JSON string")
    model_list: Optional[List[str]] = Field([], description="List of model names")
    selected_model: Optional[str] = Field(None, description="Currently selected model name")
    is_primary: Optional[bool] = Field(False, description="Whether this is the primary/selected provider")


class ModelProviderCreate(ModelProviderBase):
    """Schema for creating a new model provider configuration"""
    pass


class ModelProviderUpdate(ModelProviderBase):
    """Schema for updating an existing model provider configuration"""
    provider_name: Optional[str] = None


class ModelProvider(ModelProviderBase):
    """Schema for model provider with database fields"""
    id: str = Field(..., description="Unique identifier for the model provider configuration")
    created_at: str = Field(..., description="Timestamp when the configuration was created")
    updated_at: str = Field(..., description="Timestamp when the configuration was last updated")

    class Config:
        from_attributes = True


class ModelProviderResponse(BaseModel):
    """Response schema for model provider operations"""
    success: bool
    message: str
    data: Optional[ModelProvider] = None
