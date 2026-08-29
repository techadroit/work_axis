"""Gmail OAuth handshake: authorization URL construction, code exchange, and
token refresh. Uses google-auth-oauthlib/google-auth directly (not
google-api-python-client) - Gmail's own REST API is called via httpx
elsewhere (gmail_api_client.py).
"""
import datetime

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"


def _build_client_config(client_id: str, client_secret: str, redirect_uri: str) -> dict:
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
            "redirect_uris": [redirect_uri],
        }
    }


def build_authorization_url(client_id: str, client_secret: str, redirect_uri: str) -> tuple[str, str]:
    """Returns (auth_url, state). access_type=offline + prompt=consent are
    required to force Google to actually return a refresh_token."""
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        _build_client_config(client_id, client_secret, redirect_uri),
        scopes=GMAIL_SCOPES,
    )
    flow.redirect_uri = redirect_uri
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    return auth_url, state


def exchange_code_for_tokens(client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict:
    """Exchanges an authorization code for tokens.

    Returns {access_token, refresh_token, expiry (ISO str or None), scopes (space-separated str)}.
    """
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        _build_client_config(client_id, client_secret, redirect_uri),
        scopes=GMAIL_SCOPES,
    )
    flow.redirect_uri = redirect_uri
    flow.fetch_token(code=code)
    creds = flow.credentials

    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
        "scopes": " ".join(creds.scopes) if creds.scopes else "",
    }


def _parse_expiry(token_expiry) -> datetime.datetime | None:
    """Accepts either an ISO string or a datetime (DuckDB TIMESTAMP columns
    round-trip as native datetime objects, not strings, when read back)."""
    if not token_expiry:
        return None
    if isinstance(token_expiry, datetime.datetime):
        dt = token_expiry
    else:
        try:
            dt = datetime.datetime.fromisoformat(str(token_expiry))
        except ValueError:
            return None
    # google-auth's Credentials.expiry is conventionally a naive UTC datetime.
    if dt.tzinfo is not None:
        dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return dt


def get_valid_access_token(
    access_token: str,
    refresh_token: str,
    token_expiry: str | None,
    client_id: str,
    client_secret: str,
) -> dict:
    """Returns {access_token, expiry (ISO str or None), refreshed: bool}.

    Raises google.auth.exceptions.RefreshError if the refresh token has been
    revoked (invalid_grant) - callers should catch this and mark the account
    as needing re-authentication rather than crashing the sync.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=GOOGLE_TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=GMAIL_SCOPES,
        expiry=_parse_expiry(token_expiry),
    )

    if not creds.expired:
        return {"access_token": creds.token, "expiry": token_expiry, "refreshed": False}

    creds.refresh(Request())
    return {
        "access_token": creds.token,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
        "refreshed": True,
    }
