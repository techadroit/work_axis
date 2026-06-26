"""API routes for model provider configuration management"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from backend.app.server.schemas.model_provider_schemas import (
    ModelProvider,
    ModelProviderCreate,
    ModelProviderResponse
)
from backend.app.server.service.model_provider_service import provide_model_provider_service
from backend.app.utils.logger_util import log_error

model_provider_routes = APIRouter(
    prefix="/settings/providers",
    tags=["Model Providers"],
)

# Initialize service
model_provider_service = provide_model_provider_service()


@model_provider_routes.post(
    "/",
    response_model=ModelProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add or update model provider configurations"
)
def add_or_update_provider(providers: List[ModelProviderCreate]):
    """
    Add new model provider configurations or update existing ones.
    If a provider with the same name exists, it will be replaced with the new configuration.

    Args:
        providers: List of model provider configuration data

    Returns:
        ModelProviderResponse with the created/updated providers
    """
    try:
        results = []
        for provider in providers:
            result = model_provider_service.add_or_update_provider(provider)
            results.append(result)

        provider_names = ", ".join([p.provider_name for p in providers])
        return ModelProviderResponse(
            success=True,
            message=f"Successfully configured {len(providers)} provider(s): {provider_names}",
            data=results[0] if len(results) == 1 else None  # Return single provider if only one
        )
    except Exception as e:
        log_error(f"Error adding/updating providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure providers: {str(e)}"
        )


@model_provider_routes.get(
    "/",
    response_model=List[ModelProvider],
    summary="Get all model provider configurations"
)
def get_all_providers():
    """
    Retrieve all configured model providers.

    Returns:
        List of all model provider configurations
    """
    try:
        providers = model_provider_service.get_all_providers()
        return providers
    except Exception as e:
        log_error(f"Error getting all providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve providers: {str(e)}"
        )


@model_provider_routes.get(
    "/{provider_name}",
    response_model=ModelProvider,
    summary="Get model provider configuration by name"
)
def get_provider_by_name(provider_name: str):
    """
    Retrieve a specific model provider configuration by name.

    Args:
        provider_name: Name of the provider (e.g., OpenAI, Anthropic, Google)

    Returns:
        Model provider configuration
    """
    try:
        provider = model_provider_service.get_provider_by_name(provider_name)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider '{provider_name}' not found"
            )
        return provider
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error getting provider {provider_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve provider: {str(e)}"
        )


@model_provider_routes.delete(
    "/{provider_name}",
    response_model=ModelProviderResponse,
    summary="Delete model provider configuration by name"
)
def delete_provider_by_name(provider_name: str):
    """
    Delete a model provider configuration by name.

    Args:
        provider_name: Name of the provider to delete

    Returns:
        ModelProviderResponse with success status
    """
    try:
        deleted = model_provider_service.delete_provider(provider_name)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider '{provider_name}' not found"
            )
        return ModelProviderResponse(
            success=True,
            message=f"Successfully deleted {provider_name} provider configuration",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error deleting provider {provider_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete provider: {str(e)}"
        )


@model_provider_routes.delete(
    "/id/{provider_id}",
    response_model=ModelProviderResponse,
    summary="Delete model provider configuration by ID"
)
def delete_provider_by_id(provider_id: str):
    """
    Delete a model provider configuration by ID.

    Args:
        provider_id: ID of the provider to delete

    Returns:
        ModelProviderResponse with success status
    """
    try:
        deleted = model_provider_service.delete_provider_by_id(provider_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider with ID '{provider_id}' not found"
            )
        return ModelProviderResponse(
            success=True,
            message=f"Successfully deleted provider configuration",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error deleting provider by ID {provider_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete provider: {str(e)}"
        )

