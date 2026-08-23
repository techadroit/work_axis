"""Model Provider repository for managing model provider configurations"""
import json
import uuid
from typing import List, Optional

from sqlalchemy import select

from src.app.server.database.db_session import get_db_session
from src.app.server.database.orm_models import ModelProviderORM
from src.app.server.schemas.model_provider_schemas import ModelProvider, ModelProviderCreate
from src.app.utils.logger_util import log_info, log_error, log_debug
from core.utils.time_util import get_utc_time


def _to_model_provider(row: ModelProviderORM) -> ModelProvider:
    return ModelProvider(
        id=row.id,
        provider_name=row.provider_name,
        api_key=row.api_key,
        base_url=row.base_url,
        api_version=row.api_version,
        deployment_name=row.deployment_name,
        aws_access_key_id=row.aws_access_key_id,
        aws_secret_access_key=row.aws_secret_access_key,
        region=row.region,
        config_json=row.config_json,
        model_list=json.loads(row.model_list) if row.model_list else [],
        model_provider=row.model_provider,
        selected_model=row.selected_model,
        is_primary=bool(row.is_primary) if row.is_primary is not None else False,
        created_at=str(row.created_at) if row.created_at else None,
        updated_at=str(row.updated_at) if row.updated_at else None,
    )


class ModelProviderRepository:
    """Repository for managing model provider database operations"""

    @staticmethod
    def add_or_replace_provider(provider_create: ModelProviderCreate) -> ModelProvider:
        """
        Add a new model provider configuration or replace existing one with the same provider_name.

        Args:
            provider_create: ModelProviderCreate model containing provider configuration

        Returns:
            The created/updated ModelProvider

        Raises:
            Exception: If operation fails
        """
        try:
            model_list = json.dumps(provider_create.model_list)
            current_time = get_utc_time()

            with get_db_session() as session:
                existing = session.execute(
                    select(ModelProviderORM).where(
                        ModelProviderORM.provider_name == provider_create.provider_name
                    )
                ).scalar_one_or_none()

                if existing:
                    existing.api_key = provider_create.api_key
                    existing.base_url = provider_create.base_url
                    existing.api_version = provider_create.api_version
                    existing.deployment_name = provider_create.deployment_name
                    existing.aws_access_key_id = provider_create.aws_access_key_id
                    existing.aws_secret_access_key = provider_create.aws_secret_access_key
                    existing.region = provider_create.region
                    existing.config_json = provider_create.config_json
                    existing.model_list = model_list
                    existing.model_provider = provider_create.model_provider
                    existing.selected_model = provider_create.selected_model
                    existing.is_primary = provider_create.is_primary
                    existing.updated_at = current_time
                    provider_id = existing.id
                    log_info(f"Updated model provider: {provider_create.provider_name}")
                else:
                    provider_id = str(uuid.uuid4())
                    new_provider = ModelProviderORM(
                        id=provider_id,
                        provider_name=provider_create.provider_name,
                        api_key=provider_create.api_key,
                        base_url=provider_create.base_url,
                        api_version=provider_create.api_version,
                        deployment_name=provider_create.deployment_name,
                        aws_access_key_id=provider_create.aws_access_key_id,
                        aws_secret_access_key=provider_create.aws_secret_access_key,
                        region=provider_create.region,
                        config_json=provider_create.config_json,
                        model_list=model_list,
                        model_provider=provider_create.model_provider,
                        selected_model=provider_create.selected_model,
                        is_primary=provider_create.is_primary,
                        created_at=current_time,
                        updated_at=current_time,
                    )
                    session.add(new_provider)
                    log_info(f"Created new model provider: {provider_create.provider_name}")

                session.flush()
                result = session.get(ModelProviderORM, provider_id)

                if result:
                    return _to_model_provider(result)
                raise Exception("Failed to retrieve created/updated provider")

        except Exception as e:
            log_error(f"Error adding/replacing model provider: {e}")
            raise

    @staticmethod
    def get_primary_provider() -> Optional[ModelProvider]:
        """
        Get the primary model provider configuration.

        Returns:
            ModelProvider or None if no primary provider is set
        """
        try:
            with get_db_session() as session:
                result = session.execute(
                    select(ModelProviderORM).where(ModelProviderORM.is_primary == 1).limit(1)
                ).scalar_one_or_none()

                return _to_model_provider(result) if result else None

        except Exception as e:
            log_error(f"Error getting model provider by name: {e}")
            raise

    @staticmethod
    def get_provider_by_name(provider_name: str) -> Optional[ModelProvider]:
        """
        Get a model provider configuration by provider name.

        Args:
            provider_name: The name of the provider to retrieve

        Returns:
            ModelProvider or None if not found
        """
        try:
            with get_db_session() as session:
                result = session.execute(
                    select(ModelProviderORM).where(ModelProviderORM.provider_name == provider_name)
                ).scalar_one_or_none()

                return _to_model_provider(result) if result else None

        except Exception as e:
            log_error(f"Error getting model provider by name: {e}")
            raise

    @staticmethod
    def get_all_providers() -> List[ModelProvider]:
        """
        Get all model provider configurations.

        Returns:
            List of ModelProvider objects
        """
        try:
            with get_db_session() as session:
                results = session.execute(
                    select(ModelProviderORM).order_by(ModelProviderORM.created_at.desc())
                ).scalars().all()

                providers = [_to_model_provider(row) for row in results]

            log_debug(f"Retrieved {len(providers)} model providers")
            return providers

        except Exception as e:
            log_error(f"Error getting all model providers: {e}")
            raise

    @staticmethod
    def delete_provider(provider_name: str) -> bool:
        """
        Delete a model provider configuration by provider name.

        Args:
            provider_name: The name of the provider to delete

        Returns:
            True if deleted successfully, False if not found

        Raises:
            Exception: If deletion fails
        """
        try:
            with get_db_session() as session:
                existing = session.execute(
                    select(ModelProviderORM).where(ModelProviderORM.provider_name == provider_name)
                ).scalar_one_or_none()

                if not existing:
                    log_debug(f"Model provider not found: {provider_name}")
                    return False

                session.delete(existing)

            log_info(f"Deleted model provider: {provider_name}")
            return True

        except Exception as e:
            log_error(f"Error deleting model provider: {e}")
            raise

    @staticmethod
    def delete_provider_by_id(provider_id: str) -> bool:
        """
        Delete a model provider configuration by ID.

        Args:
            provider_id: The ID of the provider to delete

        Returns:
            True if deleted successfully, False if not found

        Raises:
            Exception: If deletion fails
        """
        try:
            with get_db_session() as session:
                existing = session.get(ModelProviderORM, provider_id)

                if not existing:
                    log_debug(f"Model provider not found with ID: {provider_id}")
                    return False

                session.delete(existing)

            log_info(f"Deleted model provider with ID: {provider_id}")
            return True

        except Exception as e:
            log_error(f"Error deleting model provider by ID: {e}")
            raise
