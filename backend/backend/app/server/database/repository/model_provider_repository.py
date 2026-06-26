"""Model Provider repository for managing model provider configurations"""
import json
import uuid
from typing import List, Optional

from backend.app.server.database.db_session import get_db_connection, TABLE_MODEL_PROVIDERS
from backend.app.server.schemas.model_provider_schemas import ModelProvider, ModelProviderCreate
from backend.app.utils.logger_util import log_info, log_error, log_debug
from core.utils.time_util import get_utc_time


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
            conn = get_db_connection()
            model_list = json.dumps(provider_create.model_list)

            # Check if provider with this name already exists
            existing = conn.execute(f"""
                SELECT id FROM {TABLE_MODEL_PROVIDERS}
                WHERE provider_name = ?
            """, [provider_create.provider_name]).fetchone()

            provider_id = existing[0] if existing else str(uuid.uuid4())
            current_time = get_utc_time()

            if existing:
                # Update existing provider
                conn.execute(f"""
                    UPDATE {TABLE_MODEL_PROVIDERS}
                    SET api_key = ?,
                        base_url = ?,
                        api_version = ?,
                        deployment_name = ?,
                        aws_access_key_id = ?,
                        aws_secret_access_key = ?,
                        region = ?,
                        config_json = ?,
                        model_list = ?,
                        model_provider = ?,
                        selected_model = ?,
                        is_primary = ?,
                        updated_at = ?
                    WHERE id = ?
                """, [
                    provider_create.api_key,
                    provider_create.base_url,
                    provider_create.api_version,
                    provider_create.deployment_name,
                    provider_create.aws_access_key_id,
                    provider_create.aws_secret_access_key,
                    provider_create.region,
                    provider_create.config_json,
                    model_list,
                    provider_create.model_provider,
                    provider_create.selected_model,
                    provider_create.is_primary,
                    current_time,
                    provider_id
                ])
                log_info(f"Updated model provider: {provider_create.provider_name}")
            else:
                # Insert new provider
                conn.execute(f"""
                    INSERT INTO {TABLE_MODEL_PROVIDERS} (
                        id, provider_name, api_key, base_url, api_version,
                        deployment_name, aws_access_key_id, aws_secret_access_key,
                        region, config_json, model_list, model_provider, selected_model, is_primary, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    provider_id,
                    provider_create.provider_name,
                    provider_create.api_key,
                    provider_create.base_url,
                    provider_create.api_version,
                    provider_create.deployment_name,
                    provider_create.aws_access_key_id,
                    provider_create.aws_secret_access_key,
                    provider_create.region,
                    provider_create.config_json,
                    model_list,
                    provider_create.model_provider,
                    provider_create.selected_model,
                    provider_create.is_primary,
                    current_time,
                    current_time
                ])
                log_info(f"Created new model provider: {provider_create.provider_name}")

            # Fetch and return the created/updated provider
            result = conn.execute(f"""
                SELECT id, provider_name, api_key, base_url, api_version,
                       deployment_name, aws_access_key_id, aws_secret_access_key,
                       region, config_json, model_list, model_provider, selected_model, is_primary, created_at, updated_at
                FROM {TABLE_MODEL_PROVIDERS}
                WHERE id = ?
            """, [provider_id]).fetchone()

            conn.close()

            if result:
                return ModelProvider(
                    id=result[0],
                    provider_name=result[1],
                    api_key=result[2],
                    base_url=result[3],
                    api_version=result[4],
                    deployment_name=result[5],
                    aws_access_key_id=result[6],
                    aws_secret_access_key=result[7],
                    region=result[8],
                    config_json=result[9],
                    model_list = json.loads(result[10]) if result and result[10] else [],
                    selected_model=result[11],
                    model_provider=result[12],
                    is_primary=bool(result[13]) if result[13] is not None else False,
                    created_at=str(result[14]) if result[14] else None,
                    updated_at=str(result[15]) if result[15] else None
                )
            else:
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
            conn = get_db_connection()

            result = conn.execute(f"""
                SELECT id, provider_name, api_key, base_url, api_version,
                       deployment_name, aws_access_key_id, aws_secret_access_key,
                       region, config_json, model_list, model_provider, selected_model, is_primary, created_at, updated_at
                FROM {TABLE_MODEL_PROVIDERS}
                WHERE is_primary = 1
                LIMIT 1
            """).fetchone()

            conn.close()

            if result:
                return ModelProvider(
                    id=result[0],
                    provider_name=result[1],
                    api_key=result[2],
                    base_url=result[3],
                    api_version=result[4],
                    deployment_name=result[5],
                    aws_access_key_id=result[6],
                    aws_secret_access_key=result[7],
                    region=result[8],
                    config_json=result[9],
                    model_list = json.loads(result[10]) if result and result[10] else [],
                    model_provider=result[11],
                    selected_model=result[12],
                    is_primary=bool(result[13]) if result[13] is not None else False,
                    created_at=str(result[14]) if result[14] else None,
                    updated_at=str(result[15]) if result[15] else None
                )
            return None

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
            conn = get_db_connection()

            result = conn.execute(f"""
                SELECT id, provider_name, api_key, base_url, api_version,
                       deployment_name, aws_access_key_id, aws_secret_access_key,
                       region, config_json, model_list, model_provider, selected_model, is_primary, created_at, updated_at
                FROM {TABLE_MODEL_PROVIDERS}
                WHERE provider_name = ?
            """, [provider_name]).fetchone()

            conn.close()

            if result:
                return ModelProvider(
                    id=result[0],
                    provider_name=result[1],
                    api_key=result[2],
                    base_url=result[3],
                    api_version=result[4],
                    deployment_name=result[5],
                    aws_access_key_id=result[6],
                    aws_secret_access_key=result[7],
                    region=result[8],
                    config_json=result[9],
                    model_list = json.loads(result[10]) if result and result[10] else [],
                    model_provider=result[11],
                    selected_model=result[12],
                    is_primary=bool(result[13]) if result[13] is not None else False,
                    created_at=str(result[14]) if result[14] else None,
                    updated_at=str(result[15]) if result[15] else None
                )
            return None

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
            conn = get_db_connection()

            results = conn.execute(f"""
                SELECT id, provider_name, api_key, base_url, api_version,
                       deployment_name, aws_access_key_id, aws_secret_access_key,
                       region, config_json, model_list, model_provider, selected_model, is_primary, created_at, updated_at
                FROM {TABLE_MODEL_PROVIDERS}
                ORDER BY created_at DESC
            """).fetchall()

            conn.close()

            providers = []
            for row in results:
                providers.append(ModelProvider(
                    id=row[0],
                    provider_name=row[1],
                    api_key=row[2],
                    base_url=row[3],
                    api_version=row[4],
                    deployment_name=row[5],
                    aws_access_key_id=row[6],
                    aws_secret_access_key=row[7],
                    region=row[8],
                    config_json=row[9],
                    model_list = json.loads(row[10]) if row and row[10] else [],
                    model_provider=row[11],
                    selected_model=row[12],
                    is_primary=bool(row[13]) if row[13] is not None else False,
                    created_at=str(row[14]) if row[14] else None,
                    updated_at=str(row[15]) if row[15] else None
                ))

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
            conn = get_db_connection()

            # Check if exists
            existing = conn.execute(f"""
                SELECT id FROM {TABLE_MODEL_PROVIDERS}
                WHERE provider_name = ?
            """, [provider_name]).fetchone()

            if not existing:
                conn.close()
                log_debug(f"Model provider not found: {provider_name}")
                return False

            # Delete the provider
            conn.execute(f"""
                DELETE FROM {TABLE_MODEL_PROVIDERS}
                WHERE provider_name = ?
            """, [provider_name])

            conn.close()
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
            conn = get_db_connection()

            # Check if exists
            existing = conn.execute(f"""
                SELECT id FROM {TABLE_MODEL_PROVIDERS}
                WHERE id = ?
            """, [provider_id]).fetchone()

            if not existing:
                conn.close()
                log_debug(f"Model provider not found with ID: {provider_id}")
                return False

            # Delete the provider
            conn.execute(f"""
                DELETE FROM {TABLE_MODEL_PROVIDERS}
                WHERE id = ?
            """, [provider_id])

            conn.close()
            log_info(f"Deleted model provider with ID: {provider_id}")
            return True

        except Exception as e:
            log_error(f"Error deleting model provider by ID: {e}")
            raise

