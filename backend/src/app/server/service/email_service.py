"""Service layer for email integration (provider credentials + connected accounts).

Covers: credential CRUD, the Gmail OAuth handshake (Phase 2), and token
refresh. Ingestion (Phase 3), manual sync execution (Phase 4), and file
import (Phase 5) build on top of this in the same file.
"""
import asyncio
import os
import threading
import time
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import UploadFile, HTTPException
from google.auth.exceptions import RefreshError

from email_ingestion.gmail.gmail_oauth_client import (
    build_authorization_url as gmail_build_authorization_url,
    exchange_code_for_tokens as gmail_exchange_code_for_tokens,
    get_valid_access_token as gmail_get_valid_access_token,
)
from email_ingestion.gmail import gmail_api_client
from email_ingestion.gmail.gmail_message_parser import parse_gmail_raw_message
from email_ingestion.file_import.mbox_parser import parse_mbox
from email_ingestion.file_import.eml_parser import parse_eml
from email_ingestion.models.email_document import EmailDocument
from core.utils.file_util import get_files_path

from src.app.server.database.repository.email_repository import (
    EmailProviderCredentialRepository,
    EmailAccountRepository,
)
from src.app.server.schemas.email_schemas import (
    EmailProviderCredentials,
    EmailProviderCredentialsCreate,
    EmailAccount,
)
from src.app.utils.env_util import load_environment
from src.app.utils.logger_util import log_error, log_info

# Short-lived, in-memory correlation of an OAuth "state" token back to the
# request that started it. Single-user desktop app - no need for real
# session/cookie infrastructure for this. Guarded by a lock because the
# routes that touch it are sync `def` endpoints, which FastAPI runs on a
# threadpool - concurrent requests mutate this dict from different threads,
# and iterating during cleanup while another thread inserts would raise
# "dictionary changed size during iteration".
_PENDING_OAUTH_STATES: dict[str, dict] = {}
_PENDING_OAUTH_STATES_LOCK = threading.Lock()
_OAUTH_STATE_TTL_SECONDS = 600


def _store_oauth_state(state: str, payload: dict) -> None:
    now = time.time()
    with _PENDING_OAUTH_STATES_LOCK:
        expired = [s for s, v in _PENDING_OAUTH_STATES.items() if now - v["created_at"] > _OAUTH_STATE_TTL_SECONDS]
        for s in expired:
            _PENDING_OAUTH_STATES.pop(s, None)
        _PENDING_OAUTH_STATES[state] = payload


def _pop_oauth_state(state: str) -> Optional[dict]:
    with _PENDING_OAUTH_STATES_LOCK:
        return _PENDING_OAUTH_STATES.pop(state, None)


# App-bundled OAuth client (Google "Desktop app" type) so end users can
# "Connect Gmail" without ever setting up their own Google Cloud project - see
# backend/environment/.env.gmail.example for how this is provisioned. Only
# used as a fallback: a provider row saved via save_provider_credentials()
# (a self-hoster's own Google Cloud project) always wins over this, checked
# by get_effective_provider_credentials() below.
_BUNDLED_ENV_LOADED = {"gmail": False}


def _get_bundled_provider_credentials(provider: str) -> Optional[dict]:
    if provider not in _BUNDLED_ENV_LOADED:
        return None
    if not _BUNDLED_ENV_LOADED[provider]:
        load_environment(f"environment/.env.{provider}")
        _BUNDLED_ENV_LOADED[provider] = True

    prefix = provider.upper()
    client_id = os.environ.get(f"{prefix}_DEFAULT_CLIENT_ID")
    client_secret = os.environ.get(f"{prefix}_DEFAULT_CLIENT_SECRET")
    redirect_uri = os.environ.get(f"{prefix}_DEFAULT_REDIRECT_URI")
    if not client_id or not client_secret or not redirect_uri:
        return None
    return {"client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri}


def build_email_ingestion_pipeline():
    """Builds the chunk -> embed -> store pipeline chain for email ingestion.

    Deliberately skips the docling LoadFilePipeline stage since email bodies
    are already plain text. Build this once per sync/import run and reuse it
    across every email in that run (collection creation + embedding-model
    resolution happen once here, not per email).
    """
    from rag.pipeline.chunking_pipeline import ChunkingPipeline
    from rag.pipeline.email_embedding_pipeline import EmailEmbeddingPipeline
    from rag.pipeline.vector_storage_pipeline import VectorStoragePipeline
    from rag.pipeline.log_pipeline import LogPipeline
    from rag.pipeline.pipeline_handler import PipelineHandler
    from vector_db.base.vector_db_config import VectorDbConfig
    from vector_db.vectordb_factory import VectorDBFactory
    from src.app.utils.embedding_util import get_cached_default_embedding_model

    embedding_model = get_cached_default_embedding_model()
    vector_db_config = VectorDbConfig()
    vector_storage = VectorStoragePipeline(
        client=VectorDBFactory.create_vectordb_client(),
        vector_db_config=vector_db_config,
        embedding_configuration=embedding_model,
        next_steps=LogPipeline(),
    )
    email_embedding = EmailEmbeddingPipeline(next_steps=vector_storage)
    return PipelineHandler(pipelines=[ChunkingPipeline(next_steps=email_embedding)])


def ingest_email_document(pipeline_handler, email_document: EmailDocument, user_id: str, email_account_id: str) -> None:
    """Ingests one EmailDocument through the pipeline built by
    build_email_ingestion_pipeline(). Synchronous - safe to call from a plain
    loop inside an asyncio.to_thread() worker (PipelineHandler.start() is
    declared async but does no actual awaiting internally, so asyncio.run()
    here is just a way to invoke it, not real concurrency)."""
    if not email_document.body_text.strip():
        return
    metadata = {
        "source": "email",
        "user_id": str(user_id),
        "email_account_id": str(email_account_id),
        "message_id": str(email_document.message_id),
        "from": str(email_document.from_addr or ""),
        "subject": str(email_document.subject or ""),
        "date": str(email_document.date or ""),
    }
    asyncio.run(pipeline_handler.start(data=[email_document.body_text], email_metadata=metadata))


_ALLOWED_IMPORT_EXTENSIONS = {".mbox", ".eml"}


async def save_email_import_file(file: UploadFile) -> str:
    """Saves an uploaded .mbox/.eml file to data/files.

    Deliberately does NOT reuse UploadFileHandler - its ALLOWED_MIME
    allowlist doesn't include message/rfc822 or .mbox, and browsers/Electron
    file pickers frequently report application/octet-stream for these
    anyway, so MIME sniffing isn't reliable here. Validates by extension
    instead, and keeps the general document-upload allowlist untouched.
    """
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _ALLOWED_IMPORT_EXTENSIONS:
        raise HTTPException(status_code=415, detail=f"Unsupported file type '{ext}' - expected .mbox or .eml")

    upload_dir = get_files_path()
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{uuid4().hex}{ext}"

    try:
        content = await file.read()
        file_path.write_bytes(content)
    finally:
        await file.close()

    return str(file_path)


class EmailService:
    def __init__(
        self,
        credential_repository: EmailProviderCredentialRepository,
        account_repository: EmailAccountRepository,
    ):
        self.credential_repository = credential_repository
        self.account_repository = account_repository

    def save_provider_credentials(self, credentials: EmailProviderCredentialsCreate) -> EmailProviderCredentials:
        try:
            return self.credential_repository.upsert(credentials)
        except Exception as e:
            log_error(f"Service error saving email provider credentials: {e}")
            raise

    def get_provider_credentials(self, provider: str) -> Optional[EmailProviderCredentials]:
        try:
            return self.credential_repository.get_by_provider(provider)
        except Exception as e:
            log_error(f"Service error getting email provider credentials: {e}")
            raise

    def get_effective_provider_credentials(self, provider: str) -> Optional[dict]:
        """{client_id, client_secret, redirect_uri} to actually use for this
        provider's OAuth flow. A custom Client ID/Secret saved via
        save_provider_credentials() (a self-hoster's own Google Cloud
        project) always wins; otherwise falls back to the app's bundled
        default client so Gmail works with zero per-user setup."""
        try:
            creds = self.credential_repository.get_decrypted_secret(provider)
            if creds:
                return creds
            return _get_bundled_provider_credentials(provider)
        except Exception as e:
            log_error(f"Service error resolving effective email provider credentials: {e}")
            raise

    def get_provider_status(self, provider: str) -> dict:
        """Tells the frontend whether `provider` can be connected right now,
        and whether that's via the app's bundled default client or a
        self-hosted custom one - determines whether to show the manual
        Client ID/Secret entry form at all."""
        try:
            if self.credential_repository.get_decrypted_secret(provider):
                return {"provider": provider, "available": True, "source": "custom"}
            if _get_bundled_provider_credentials(provider):
                return {"provider": provider, "available": True, "source": "bundled"}
            return {"provider": provider, "available": False, "source": "none"}
        except Exception as e:
            log_error(f"Service error getting email provider status: {e}")
            raise

    def get_accounts_for_user(self, user_id: str) -> List[EmailAccount]:
        try:
            return self.account_repository.get_all_by_user(user_id)
        except Exception as e:
            log_error(f"Service error getting email accounts: {e}")
            raise

    def get_account(self, account_id: str) -> Optional[EmailAccount]:
        try:
            return self.account_repository.get_by_id(account_id)
        except Exception as e:
            log_error(f"Service error getting email account: {e}")
            raise

    def disconnect_account(self, account_id: str) -> bool:
        """Disconnects an account AND purges its ingested email vectors -
        "disconnect" means "forget my email", not just "stop syncing"."""
        try:
            from vector_db.base.vector_db_config import VectorDbConfig
            from vector_db.vectordb_factory import VectorDBFactory

            vector_db_config = VectorDbConfig()
            vector_db = VectorDBFactory.create_vectordb_client(vector_db_config=vector_db_config)
            try:
                vector_db.delete_by_filter(
                    collection_name=vector_db_config.get_collection_name(),
                    filter_query={"email_account_id": {"$eq": account_id}},
                )
            except Exception as e:
                # Don't let a vector-store hiccup block removing the account
                # itself, but surface it loudly since data may be orphaned.
                log_error(f"Failed to purge vectors for email account {account_id}: {e}")

            return self.account_repository.delete(account_id)
        except Exception as e:
            log_error(f"Service error disconnecting email account: {e}")
            raise

    # ---------------------------------------------------------------
    # Gmail OAuth flow
    # ---------------------------------------------------------------

    def build_authorization_url(self, provider: str, user_id: str) -> dict:
        """Builds the Google consent URL. Raises ValueError if neither a
        custom nor a bundled default Client ID/Secret is available."""
        creds = self.get_effective_provider_credentials(provider)
        if not creds:
            raise ValueError(
                f"No OAuth Client ID/Secret configured for provider '{provider}'. "
                f"This app has no bundled default for it either - save your own via "
                f"POST /api/email/provider-credentials."
            )

        auth_url, state = gmail_build_authorization_url(
            creds["client_id"], creds["client_secret"], creds["redirect_uri"]
        )

        _store_oauth_state(state, {
            "provider": provider,
            "user_id": user_id,
            "created_at": time.time(),
        })
        return {"auth_url": auth_url, "state": state}

    def complete_authorization(self, code: str, state: str) -> EmailAccount:
        """Exchanges the authorization code for tokens and persists the
        connected account. Called from the OAuth redirect callback route."""
        pending = _pop_oauth_state(state)
        if not pending:
            raise ValueError("Unknown or expired OAuth state - please try connecting again.")

        provider = pending["provider"]
        user_id = pending["user_id"]

        creds = self.get_effective_provider_credentials(provider)
        if not creds:
            raise ValueError(f"OAuth Client ID/Secret for provider '{provider}' are no longer configured.")

        tokens = gmail_exchange_code_for_tokens(
            creds["client_id"], creds["client_secret"], creds["redirect_uri"], code
        )
        if not tokens.get("refresh_token"):
            log_info(
                "Gmail did not return a refresh_token - this happens if consent was previously "
                "granted without prompt=consent. The account will still connect but background "
                "sync will fail once the access token expires until re-authorized."
            )

        profile = gmail_api_client.get_profile(tokens["access_token"])
        email_address = profile["emailAddress"]

        return self.account_repository.create_or_update(
            user_id=user_id,
            provider=provider,
            email_address=email_address,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            token_expiry=tokens.get("expiry"),
            scopes=tokens.get("scopes"),
            display_name=email_address,
        )

    def get_valid_access_token_for_account(self, account_id: str) -> str:
        """Returns a valid (refreshed if necessary) access token for a
        connected account. Persists the refreshed token back to storage.
        Marks the account 'reauth_required' and re-raises if the refresh
        token has been revoked."""
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Email account not found: {account_id}")

        creds = self.get_effective_provider_credentials(account.provider)
        if not creds:
            raise ValueError(f"OAuth Client ID/Secret for provider '{account.provider}' are no longer configured.")

        tokens = self.account_repository.get_decrypted_tokens(account_id)
        if not tokens or not tokens.get("refresh_token"):
            raise ValueError(f"No refresh token stored for account {account_id} - reconnect required.")

        try:
            result = gmail_get_valid_access_token(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expiry=tokens["token_expiry"],
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
            )
        except RefreshError as e:
            self.account_repository.set_status(account_id, "reauth_required")
            log_error(f"Gmail token refresh failed for account {account_id}, marking reauth_required: {e}")
            raise

        if result["refreshed"]:
            self.account_repository.update_tokens(account_id, result["access_token"], result["expiry"])

        return result["access_token"]

    # ---------------------------------------------------------------
    # Manual sync (Phase 4)
    # ---------------------------------------------------------------

    def start_sync(self, account_id: str) -> EmailAccount:
        """Validates the account can be synced and marks it 'running'.
        Raises ValueError if not found, RuntimeError if already running."""
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Email account not found: {account_id}")
        if account.last_sync_status == "running":
            raise RuntimeError("Sync already in progress for this account")

        self.account_repository.update_sync_status(account_id, status="running", last_sync_error=None)
        return account

    def run_gmail_sync(self, account_id: str) -> None:
        """The actual sync work - intended to be run via
        asyncio.create_task(asyncio.to_thread(email_service.run_gmail_sync, account_id))
        so the CPU-bound embedding work and network-bound Gmail paging don't
        block the event loop. Full mailbox re-fetch every run (no incremental
        sync yet) - matches the "manual sync only, keep it simple" v1 scope."""
        account = self.account_repository.get_by_id(account_id)
        if not account:
            log_error(f"run_gmail_sync: account not found {account_id}")
            return

        try:
            access_token = self.get_valid_access_token_for_account(account_id)
            pipeline = build_email_ingestion_pipeline()

            total_synced = 0
            page_token = None
            while True:
                page = gmail_api_client.list_message_ids(access_token, page_token=page_token, max_results=100)
                for message_id in page["ids"]:
                    raw = gmail_api_client.get_message_raw(access_token, message_id)
                    email_document = parse_gmail_raw_message(raw)
                    ingest_email_document(
                        pipeline, email_document, user_id=account.user_id, email_account_id=account_id
                    )
                    total_synced += 1
                    if total_synced % 10 == 0:
                        self.account_repository.update_sync_status(
                            account_id, status="running", total_messages_synced=total_synced
                        )

                page_token = page["next_page_token"]
                if not page_token:
                    break

            self.account_repository.update_sync_status(
                account_id, status="success", total_messages_synced=total_synced, mark_synced_now=True
            )
            log_info(f"Gmail sync completed for account {account_id}: {total_synced} messages")
        except RefreshError as e:
            # get_valid_access_token_for_account already marked account.status
            # 'reauth_required'; last_sync_status is a separate field the
            # frontend polls, and must also be updated or it stays 'running'
            # forever.
            self.account_repository.update_sync_status(
                account_id, status="error", last_sync_error=f"Re-authentication required: {e}"
            )
        except Exception as e:
            log_error(f"Gmail sync failed for account {account_id}: {e}")
            self.account_repository.update_sync_status(account_id, status="error", last_sync_error=str(e))

    def get_sync_status(self, account_id: str) -> Optional[EmailAccount]:
        try:
            return self.account_repository.get_by_id(account_id)
        except Exception as e:
            log_error(f"Service error getting email sync status: {e}")
            raise

    # ---------------------------------------------------------------
    # File import (Phase 5) - .mbox / .eml, reuses the same ingestion
    # pipeline as Gmail sync via a shared 'file_import' account row.
    # ---------------------------------------------------------------

    def start_file_import(self, user_id: str, original_filename: str) -> EmailAccount:
        """Creates (or reuses, if the same filename was imported before) a
        'file_import' account row and marks it 'running'. The actual parse +
        ingest work happens in run_file_import(), scheduled by the route."""
        account = self.account_repository.create_or_update(
            user_id=user_id,
            provider="file_import",
            email_address=original_filename,
            display_name=original_filename,
        )
        self.account_repository.update_sync_status(account.id, status="running", last_sync_error=None)
        return account

    def run_file_import(self, account_id: str, file_path: str) -> None:
        account = self.account_repository.get_by_id(account_id)
        if not account:
            log_error(f"run_file_import: account not found {account_id}")
            return

        try:
            ext = Path(file_path).suffix.lower()
            if ext == ".mbox":
                documents = parse_mbox(file_path)
            elif ext == ".eml":
                documents = parse_eml(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            pipeline = build_email_ingestion_pipeline()
            total_synced = 0
            for document in documents:
                ingest_email_document(pipeline, document, user_id=account.user_id, email_account_id=account_id)
                total_synced += 1
                if total_synced % 10 == 0:
                    self.account_repository.update_sync_status(
                        account_id, status="running", total_messages_synced=total_synced
                    )

            self.account_repository.update_sync_status(
                account_id, status="success", total_messages_synced=total_synced, mark_synced_now=True
            )
            log_info(f"File import completed for account {account_id}: {total_synced} messages")
        except Exception as e:
            log_error(f"File import failed for account {account_id}: {e}")
            self.account_repository.update_sync_status(account_id, status="error", last_sync_error=str(e))
        finally:
            # The upload is a one-shot ingestion source, not a document the
            # user browses later - retrying means re-uploading anyway, so the
            # temp copy would just accumulate in data/files forever (a full
            # Takeout mbox can be gigabytes).
            Path(file_path).unlink(missing_ok=True)


def provide_email_service(
    credential_repository: EmailProviderCredentialRepository = None,
    account_repository: EmailAccountRepository = None,
) -> EmailService:
    if credential_repository is None:
        credential_repository = EmailProviderCredentialRepository()
    if account_repository is None:
        account_repository = EmailAccountRepository()
    return EmailService(credential_repository, account_repository)
