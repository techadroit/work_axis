import email.utils
import hashlib
from email.header import decode_header
from email.message import Message

from bs4 import BeautifulSoup

from email_ingestion.models.email_document import EmailDocument


def _decode_header_value(value: str | None) -> str:
    """Decode a MIME-encoded header (e.g. '=?UTF-8?B?...?=') into plain text."""
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for text, charset in parts:
        if isinstance(text, bytes):
            try:
                decoded.append(text.decode(charset or "utf-8", errors="replace"))
            except (LookupError, TypeError):
                decoded.append(text.decode("utf-8", errors="replace"))
        else:
            decoded.append(text)
    return "".join(decoded)


def _parse_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        if parsed is None:
            return ""
        return parsed.isoformat()
    except (TypeError, ValueError):
        return ""


def _extract_body_text(msg: Message) -> str:
    """Walk a (possibly multipart) message and return its best-effort plain text body.

    Prefers text/plain parts; falls back to stripping HTML from text/html parts.
    """
    if msg.is_multipart():
        plain_parts = []
        html_parts = []
        for part in msg.walk():
            content_type = part.get_content_type()
            if part.is_multipart():
                continue
            if part.get_content_disposition() == "attachment":
                continue
            try:
                payload = part.get_content()
            except Exception:
                continue
            if not isinstance(payload, str):
                continue
            if content_type == "text/plain":
                plain_parts.append(payload)
            elif content_type == "text/html":
                html_parts.append(payload)

        if plain_parts:
            return "\n".join(plain_parts).strip()
        if html_parts:
            return "\n".join(
                BeautifulSoup(html, "html.parser").get_text(separator="\n")
                for html in html_parts
            ).strip()
        return ""

    try:
        payload = msg.get_content()
    except Exception:
        return ""
    if not isinstance(payload, str):
        return ""
    if msg.get_content_type() == "text/html":
        return BeautifulSoup(payload, "html.parser").get_text(separator="\n").strip()
    return payload.strip()


def _fallback_message_id(msg: Message) -> str:
    """Some malformed/exported emails lack a Message-ID header. Derive a stable
    one from other headers so the ingestion pipeline's deterministic-id
    computation always has something usable (avoids duplicate ingestion on
    resync just because a real Message-ID was missing).
    """
    seed = f"{msg.get('From', '')}|{msg.get('Date', '')}|{msg.get('Subject', '')}"
    return "generated-" + hashlib.sha256(seed.encode("utf-8", errors="ignore")).hexdigest()[:32]


def extract_email_document(msg: Message, source: str = "email") -> EmailDocument:
    """Shared normalization used by BOTH the Gmail ingestion path and the
    .mbox/.eml file-import path, so there is exactly one place that decides
    what counts as an email's subject/body/date/etc.
    """
    message_id = (msg.get("Message-ID") or "").strip()
    if not message_id:
        message_id = _fallback_message_id(msg)

    to_header = msg.get("To", "")
    to_addrs = [addr.strip() for addr in to_header.split(",") if addr.strip()] if to_header else []

    return EmailDocument(
        message_id=message_id,
        thread_id=None,
        from_addr=_decode_header_value(msg.get("From", "")),
        to_addrs=to_addrs,
        subject=_decode_header_value(msg.get("Subject", "")),
        date=_parse_date(msg.get("Date")),
        body_text=_extract_body_text(msg),
        source=source,
    )
