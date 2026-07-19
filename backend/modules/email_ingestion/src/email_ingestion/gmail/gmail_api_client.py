"""Thin Gmail REST API wrapper using httpx (not google-api-python-client -
keeps the dependency footprint small, matches the httpx-based pattern
already used elsewhere in this codebase, e.g. the web-search tool)."""
import base64

import httpx

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def get_profile(access_token: str) -> dict:
    """Returns the connected mailbox's profile, notably `emailAddress`."""
    response = httpx.get(f"{GMAIL_API_BASE}/profile", headers=_headers(access_token), timeout=30)
    response.raise_for_status()
    return response.json()


def list_message_ids(access_token: str, page_token: str | None = None, max_results: int = 100) -> dict:
    """Returns {"ids": [...], "next_page_token": str | None}."""
    params = {"maxResults": max_results}
    if page_token:
        params["pageToken"] = page_token
    response = httpx.get(f"{GMAIL_API_BASE}/messages", headers=_headers(access_token), params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    ids = [m["id"] for m in data.get("messages", [])]
    return {"ids": ids, "next_page_token": data.get("nextPageToken")}


def get_message_raw(access_token: str, message_id: str) -> bytes:
    """Fetches a single message in raw RFC822 format (base64url-encoded) and
    returns the decoded raw bytes, ready for email.message_from_bytes()."""
    response = httpx.get(
        f"{GMAIL_API_BASE}/messages/{message_id}",
        headers=_headers(access_token),
        params={"format": "raw"},
        timeout=30,
    )
    response.raise_for_status()
    raw_b64 = response.json()["raw"]
    return base64.urlsafe_b64decode(raw_b64 + "=" * (-len(raw_b64) % 4))
