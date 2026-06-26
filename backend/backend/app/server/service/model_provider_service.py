"""Service layer for model provider operations"""
from typing import List, Optional

from backend.app.server.database.repository.model_provider_repository import ModelProviderRepository
from backend.app.server.schemas.model_provider_schemas import ModelProvider, ModelProviderCreate
from backend.app.utils.logger_util import log_error


class ModelProviderService:
    """Service for managing model provider configurations"""

    def __init__(self, repository: ModelProviderRepository):
        self.repository = repository

    def add_or_update_provider(self, provider_data: ModelProviderCreate) -> ModelProvider:
        """
        Add a new provider or update existing one with the same name.

        Args:
            provider_data: Provider configuration data

        Returns:
            Created/updated ModelProvider
        """
        try:
            return self.repository.add_or_replace_provider(provider_data)
        except Exception as e:
            log_error(f"Service error adding/updating provider: {e}")
            raise

    def get_provider_by_name(self, provider_name: str) -> Optional[ModelProvider]:
        """
        Get provider configuration by name.

        Args:
            provider_name: Name of the provider

        Returns:
            ModelProvider or None if not found
        """
        try:
            return self.repository.get_provider_by_name(provider_name)
        except Exception as e:
            log_error(f"Service error getting provider: {e}")
            raise

    def get_all_providers(self) -> List[ModelProvider]:
        """
        Get all provider configurations.

        Returns:
            List of ModelProvider objects
        """
        try:
            return self.repository.get_all_providers()
        except Exception as e:
            log_error(f"Service error getting all providers: {e}")
            raise

    def get_primary_provider(self) -> Optional[ModelProvider]:
        """
        Get the primary provider configuration.

        Returns:
            ModelProvider or None if no primary provider is set
        """
        try:
            return self.repository.get_primary_provider()
        except Exception as e:
            log_error(f"Service error getting primary provider: {e}")
            raise

    def delete_provider(self, provider_name: str) -> bool:
        """
        Delete a provider configuration by name.

        Args:
            provider_name: Name of the provider to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            return self.repository.delete_provider(provider_name)
        except Exception as e:
            log_error(f"Service error deleting provider: {e}")
            raise

    def delete_provider_by_id(self, provider_id: str) -> bool:
        """
        Delete a provider configuration by ID.

        Args:
            provider_id: ID of the provider to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            return self.repository.delete_provider_by_id(provider_id)
        except Exception as e:
            log_error(f"Service error deleting provider by ID: {e}")
            raise


def provide_model_provider_service(repository: ModelProviderRepository = None) -> ModelProviderService:
    """
    Dependency injection for ModelProviderService.

    Args:
        repository: Optional repository instance (creates new if not provided)

    Returns:
        ModelProviderService instance
    """
    if repository is None:
        repository = ModelProviderRepository()
    return ModelProviderService(repository)

