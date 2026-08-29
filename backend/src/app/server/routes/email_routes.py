"""API routes for email integration: Gmail OAuth connect/list/disconnect,
provider credential configuration, manual sync, and file import."""
import asyncio
import html

from fastapi import APIRouter, HTTPException, UploadFile, Form, status
from fastapi.responses import HTMLResponse
from typing import List

from src.app.server.schemas.email_schemas import (
    EmailProviderCredentials,
    EmailProviderCredentialsCreate,
    EmailProviderStatus,
    EmailAccount,
    EmailAccountResponse,
    EmailSyncStatusResponse,
)
from src.app.server.service.email_service import provide_email_service, save_email_import_file
from src.app.utils.logger_util import log_error

email_routes = APIRouter(
    prefix="/email",
    tags=["Email Integrations"],
)

email_service = provide_email_service()


# ---------------------------------------------------------------
# Provider credentials (the user's own Google OAuth Client ID/Secret)
# ---------------------------------------------------------------

@email_routes.post("/provider-credentials", response_model=EmailProviderCredentials, status_code=status.HTTP_201_CREATED)
def save_provider_credentials(credentials: EmailProviderCredentialsCreate):
    try:
        return email_service.save_provider_credentials(credentials)
    except Exception as e:
        log_error(f"Error saving email provider credentials: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@email_routes.get("/provider-credentials/{provider}", response_model=EmailProviderCredentials)
def get_provider_credentials(provider: str):
    try:
        creds = email_service.get_provider_credentials(provider)
        if not creds:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No credentials configured for '{provider}'")
        return creds
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error getting email provider credentials: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@email_routes.get("/provider-status/{provider}", response_model=EmailProviderStatus)
def get_provider_status(provider: str):
    """Tells the frontend whether `provider` is ready to connect right now
    (via the app's bundled default OAuth client or a self-hosted custom one),
    so it knows whether the manual Client ID/Secret form needs to be shown."""
    try:
        return email_service.get_provider_status(provider)
    except Exception as e:
        log_error(f"Error getting email provider status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ---------------------------------------------------------------
# Gmail OAuth connect flow
# ---------------------------------------------------------------

@email_routes.get("/{user_id}/oauth-url")
def get_oauth_url(user_id: str, provider: str = "gmail"):
    try:
        return email_service.build_authorization_url(provider, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_error(f"Error building email OAuth URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@email_routes.get("/oauth/callback", response_class=HTMLResponse)
def oauth_callback(code: str = None, state: str = None, error: str = None):
    # This page renders values that originate outside our control (query
    # params, provider error text, the connected mailbox address) - escape
    # everything interpolated into the HTML to avoid reflected XSS.
    if error:
        return HTMLResponse(
            f"<html><body><h3>Gmail connection failed</h3><p>{html.escape(error)}</p></body></html>",
            status_code=400,
        )
    if not code or not state:
        return HTMLResponse("<html><body><h3>Missing code/state</h3></body></html>", status_code=400)

    try:
        account = email_service.complete_authorization(code, state)
        return HTMLResponse(
            f"<html><body><h3>Gmail connected: {html.escape(account.email_address)}</h3>"
            f"<p>You can close this tab and return to the app.</p></body></html>"
        )
    except ValueError as e:
        return HTMLResponse(
            f"<html><body><h3>Gmail connection failed</h3><p>{html.escape(str(e))}</p></body></html>",
            status_code=400,
        )
    except Exception as e:
        log_error(f"Error completing email OAuth: {e}")
        return HTMLResponse(
            "<html><body><h3>Gmail connection failed</h3><p>An unexpected error occurred. "
            "Please close this tab and try again.</p></body></html>", status_code=500
        )


# ---------------------------------------------------------------
# Connected accounts
# ---------------------------------------------------------------

@email_routes.get("/accounts/{user_id}", response_model=List[EmailAccount])
def get_accounts(user_id: str):
    try:
        return email_service.get_accounts_for_user(user_id)
    except Exception as e:
        log_error(f"Error getting email accounts: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@email_routes.delete("/accounts/id/{account_id}", response_model=EmailAccountResponse)
def disconnect_account(account_id: str):
    try:
        deleted = email_service.disconnect_account(account_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email account '{account_id}' not found")
        return EmailAccountResponse(success=True, message="Email account disconnected", data=None)
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error disconnecting email account: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ---------------------------------------------------------------
# Manual sync
# ---------------------------------------------------------------

@email_routes.post("/accounts/id/{account_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def start_sync(account_id: str):
    # Must be async def: plain `def` routes run in a worker thread via
    # Starlette's run_in_threadpool, which has no running event loop, so
    # asyncio.create_task() below would raise "no running event loop".
    try:
        email_service.start_sync(account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        log_error(f"Error starting email sync: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # CPU-bound embedding work + network-bound Gmail paging - keep off the
    # event loop, same pattern as the startup embedding-model download.
    asyncio.create_task(asyncio.to_thread(email_service.run_gmail_sync, account_id))
    return {"status": "running"}


@email_routes.get("/accounts/id/{account_id}/sync-status", response_model=EmailSyncStatusResponse)
def get_sync_status(account_id: str):
    try:
        account = email_service.get_sync_status(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email account '{account_id}' not found")
        return EmailSyncStatusResponse(
            account_id=account.id,
            status=account.last_sync_status or "idle",
            last_synced_at=account.last_synced_at,
            total_messages_synced=account.total_messages_synced,
            last_sync_error=account.last_sync_error,
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error getting email sync status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ---------------------------------------------------------------
# File import (.mbox / .eml)
# ---------------------------------------------------------------

@email_routes.post("/import-file", status_code=status.HTTP_202_ACCEPTED)
async def import_file(file: UploadFile, user_id: str = Form(...)):
    try:
        file_path = await save_email_import_file(file)
        account = email_service.start_file_import(user_id, file.filename)
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error starting email file import: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    asyncio.create_task(asyncio.to_thread(email_service.run_file_import, account.id, file_path))
    return {"status": "running", "account_id": account.id}
