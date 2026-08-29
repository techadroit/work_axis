"""Repositories for email integration: provider credentials and connected accounts.

Encryption/decryption of secrets (client_secret, access_token, refresh_token)
happens ONLY in this file - no other layer (service, route, schema) ever
touches plaintext tokens except transiently during the OAuth exchange and
Gmail API calls.
"""
import uuid
from typing import List, Optional

from src.app.server.database.db_session import (
    get_db_connection,
    TABLE_EMAIL_PROVIDER_CREDENTIALS,
    TABLE_EMAIL_ACCOUNTS,
)
from src.app.server.schemas.email_schemas import (
    EmailProviderCredentials,
    EmailProviderCredentialsCreate,
    EmailAccount,
)
from src.app.utils.crypto_util import encrypt_secret, decrypt_secret
from src.app.utils.logger_util import log_info, log_error, log_debug
from core.utils.time_util import get_utc_time


class EmailProviderCredentialRepository:
    """Repository for the user's own OAuth Client ID/Secret per provider"""

    @staticmethod
    def upsert(credentials: EmailProviderCredentialsCreate) -> EmailProviderCredentials:
        try:
            conn = get_db_connection()
            encrypted_secret = encrypt_secret(credentials.client_secret)

            existing = conn.execute(f"""
                SELECT id FROM {TABLE_EMAIL_PROVIDER_CREDENTIALS} WHERE provider = ?
            """, [credentials.provider]).fetchone()

            credential_id = existing[0] if existing else str(uuid.uuid4())
            current_time = get_utc_time()

            if existing:
                conn.execute(f"""
                    UPDATE {TABLE_EMAIL_PROVIDER_CREDENTIALS}
                    SET client_id = ?, client_secret_encrypted = ?, redirect_uri = ?, updated_at = ?
                    WHERE id = ?
                """, [credentials.client_id, encrypted_secret, credentials.redirect_uri, current_time, credential_id])
                log_info(f"Updated email provider credentials for: {credentials.provider}")
            else:
                conn.execute(f"""
                    INSERT INTO {TABLE_EMAIL_PROVIDER_CREDENTIALS} (
                        id, provider, client_id, client_secret_encrypted, redirect_uri, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [credential_id, credentials.provider, credentials.client_id, encrypted_secret,
                      credentials.redirect_uri, current_time, current_time])
                log_info(f"Created email provider credentials for: {credentials.provider}")

            conn.close()
            return EmailProviderCredentialRepository.get_by_provider(credentials.provider)
        except Exception as e:
            log_error(f"Error upserting email provider credentials: {e}")
            raise

    @staticmethod
    def get_by_provider(provider: str) -> Optional[EmailProviderCredentials]:
        try:
            conn = get_db_connection()
            result = conn.execute(f"""
                SELECT id, provider, client_id, redirect_uri, created_at, updated_at
                FROM {TABLE_EMAIL_PROVIDER_CREDENTIALS}
                WHERE provider = ?
            """, [provider]).fetchone()
            conn.close()

            if not result:
                return None
            return EmailProviderCredentials(
                id=result[0], provider=result[1], client_id=result[2], redirect_uri=result[3],
                created_at=str(result[4]), updated_at=str(result[5])
            )
        except Exception as e:
            log_error(f"Error getting email provider credentials: {e}")
            raise

    @staticmethod
    def get_decrypted_secret(provider: str) -> Optional[dict]:
        """Returns {client_id, client_secret, redirect_uri} with the secret decrypted.

        Only for internal use by the OAuth flow code - never returned via an API response.
        """
        try:
            conn = get_db_connection()
            result = conn.execute(f"""
                SELECT client_id, client_secret_encrypted, redirect_uri
                FROM {TABLE_EMAIL_PROVIDER_CREDENTIALS}
                WHERE provider = ?
            """, [provider]).fetchone()
            conn.close()

            if not result:
                return None
            return {
                "client_id": result[0],
                "client_secret": decrypt_secret(result[1]),
                "redirect_uri": result[2],
            }
        except Exception as e:
            log_error(f"Error getting decrypted email provider credentials: {e}")
            raise


class EmailAccountRepository:
    """Repository for connected mailbox instances (Gmail OAuth accounts, file imports)"""

    _COLUMNS = """id, user_id, provider, email_address, display_name, scopes, status,
                  last_sync_status, last_sync_error, last_synced_at, total_messages_synced,
                  created_at, updated_at"""

    @staticmethod
    def _row_to_account(row) -> EmailAccount:
        return EmailAccount(
            id=row[0], user_id=row[1], provider=row[2], email_address=row[3],
            display_name=row[4], scopes=row[5], status=row[6],
            last_sync_status=row[7], last_sync_error=row[8],
            last_synced_at=str(row[9]) if row[9] else None,
            total_messages_synced=row[10] or 0,
            created_at=str(row[11]), updated_at=str(row[12]),
        )

    @staticmethod
    def create_or_update(
        user_id: str,
        provider: str,
        email_address: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[str] = None,
        scopes: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> EmailAccount:
        """Create a new account, or update tokens if (user_id, provider, email_address) already exists."""
        try:
            conn = get_db_connection()
            existing = conn.execute(f"""
                SELECT id FROM {TABLE_EMAIL_ACCOUNTS}
                WHERE user_id = ? AND provider = ? AND email_address = ?
            """, [user_id, provider, email_address]).fetchone()

            current_time = get_utc_time()
            encrypted_access = encrypt_secret(access_token)
            encrypted_refresh = encrypt_secret(refresh_token)

            if existing:
                account_id = existing[0]
                conn.execute(f"""
                    UPDATE {TABLE_EMAIL_ACCOUNTS}
                    SET access_token_encrypted = ?, refresh_token_encrypted = ?, token_expiry = ?,
                        scopes = ?, display_name = ?, status = 'connected', updated_at = ?
                    WHERE id = ?
                """, [encrypted_access, encrypted_refresh, token_expiry, scopes, display_name,
                      current_time, account_id])
                log_info(f"Updated email account: {email_address}")
            else:
                account_id = str(uuid.uuid4())
                conn.execute(f"""
                    INSERT INTO {TABLE_EMAIL_ACCOUNTS} (
                        id, user_id, provider, email_address, display_name,
                        access_token_encrypted, refresh_token_encrypted, token_expiry, scopes,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'connected', ?, ?)
                """, [account_id, user_id, provider, email_address, display_name,
                      encrypted_access, encrypted_refresh, token_expiry, scopes,
                      current_time, current_time])
                log_info(f"Created new email account: {email_address}")

            conn.close()
            return EmailAccountRepository.get_by_id(account_id)
        except Exception as e:
            log_error(f"Error creating/updating email account: {e}")
            raise

    @staticmethod
    def get_by_id(account_id: str) -> Optional[EmailAccount]:
        try:
            conn = get_db_connection()
            result = conn.execute(f"""
                SELECT {EmailAccountRepository._COLUMNS} FROM {TABLE_EMAIL_ACCOUNTS} WHERE id = ?
            """, [account_id]).fetchone()
            conn.close()
            return EmailAccountRepository._row_to_account(result) if result else None
        except Exception as e:
            log_error(f"Error getting email account by id: {e}")
            raise

    @staticmethod
    def get_decrypted_tokens(account_id: str) -> Optional[dict]:
        """Returns {access_token, refresh_token, token_expiry} decrypted, for internal sync use only."""
        try:
            conn = get_db_connection()
            result = conn.execute(f"""
                SELECT access_token_encrypted, refresh_token_encrypted, token_expiry
                FROM {TABLE_EMAIL_ACCOUNTS} WHERE id = ?
            """, [account_id]).fetchone()
            conn.close()
            if not result:
                return None
            return {
                "access_token": decrypt_secret(result[0]),
                "refresh_token": decrypt_secret(result[1]),
                "token_expiry": result[2],
            }
        except Exception as e:
            log_error(f"Error getting decrypted email account tokens: {e}")
            raise

    @staticmethod
    def update_tokens(account_id: str, access_token: str, token_expiry: str) -> None:
        try:
            conn = get_db_connection()
            conn.execute(f"""
                UPDATE {TABLE_EMAIL_ACCOUNTS}
                SET access_token_encrypted = ?, token_expiry = ?, updated_at = ?
                WHERE id = ?
            """, [encrypt_secret(access_token), token_expiry, get_utc_time(), account_id])
            conn.close()
        except Exception as e:
            log_error(f"Error updating email account tokens: {e}")
            raise

    @staticmethod
    def get_all_by_user(user_id: str) -> List[EmailAccount]:
        try:
            conn = get_db_connection()
            results = conn.execute(f"""
                SELECT {EmailAccountRepository._COLUMNS} FROM {TABLE_EMAIL_ACCOUNTS}
                WHERE user_id = ? ORDER BY created_at DESC
            """, [user_id]).fetchall()
            conn.close()
            accounts = [EmailAccountRepository._row_to_account(row) for row in results]
            log_debug(f"Retrieved {len(accounts)} email accounts for user {user_id}")
            return accounts
        except Exception as e:
            log_error(f"Error getting email accounts for user: {e}")
            raise

    @staticmethod
    def update_sync_status(
        account_id: str,
        status: str,
        last_sync_error: Optional[str] = None,
        total_messages_synced: Optional[int] = None,
        mark_synced_now: bool = False,
    ) -> None:
        try:
            conn = get_db_connection()
            if mark_synced_now:
                conn.execute(f"""
                    UPDATE {TABLE_EMAIL_ACCOUNTS}
                    SET last_sync_status = ?, last_sync_error = ?,
                        total_messages_synced = COALESCE(?, total_messages_synced),
                        last_synced_at = ?, updated_at = ?
                    WHERE id = ?
                """, [status, last_sync_error, total_messages_synced, get_utc_time(), get_utc_time(), account_id])
            else:
                # Used for live progress updates mid-sync - updates the running
                # count without touching last_synced_at (only set on completion).
                conn.execute(f"""
                    UPDATE {TABLE_EMAIL_ACCOUNTS}
                    SET last_sync_status = ?, last_sync_error = ?,
                        total_messages_synced = COALESCE(?, total_messages_synced), updated_at = ?
                    WHERE id = ?
                """, [status, last_sync_error, total_messages_synced, get_utc_time(), account_id])
            conn.close()
        except Exception as e:
            log_error(f"Error updating email account sync status: {e}")
            raise

    @staticmethod
    def set_status(account_id: str, status: str) -> None:
        try:
            conn = get_db_connection()
            conn.execute(f"""
                UPDATE {TABLE_EMAIL_ACCOUNTS} SET status = ?, updated_at = ? WHERE id = ?
            """, [status, get_utc_time(), account_id])
            conn.close()
        except Exception as e:
            log_error(f"Error setting email account status: {e}")
            raise

    @staticmethod
    def delete(account_id: str) -> bool:
        try:
            conn = get_db_connection()
            existing = conn.execute(f"""
                SELECT id FROM {TABLE_EMAIL_ACCOUNTS} WHERE id = ?
            """, [account_id]).fetchone()
            if not existing:
                conn.close()
                return False
            conn.execute(f"DELETE FROM {TABLE_EMAIL_ACCOUNTS} WHERE id = ?", [account_id])
            conn.close()
            log_info(f"Deleted email account: {account_id}")
            return True
        except Exception as e:
            log_error(f"Error deleting email account: {e}")
            raise
