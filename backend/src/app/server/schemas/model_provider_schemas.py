"""Pydantic schemas for model provider configuration.

Shim – re-exports from the core module so existing imports keep working unchanged.
"""
from core.schemas.model_provider_schemas import (  # noqa: F401
    ModelProviderBase,
    ModelProviderCreate,
    ModelProviderUpdate,
    ModelProvider,
    ModelProviderResponse,
)

