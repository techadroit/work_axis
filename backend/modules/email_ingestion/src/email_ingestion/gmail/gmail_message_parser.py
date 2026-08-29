import email
import email.policy

from email_ingestion.models.email_document import EmailDocument
from email_ingestion.normalize import extract_email_document


def parse_gmail_raw_message(raw_bytes: bytes) -> EmailDocument:
    """Parses raw RFC822 bytes (as returned by gmail_api_client.get_message_raw)
    into a normalized EmailDocument, using the SAME normalization path as the
    .mbox/.eml file-import route - this is what keeps Gmail and file-import
    ingestion behaviorally identical.
    """
    msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
    return extract_email_document(msg, source="email")
