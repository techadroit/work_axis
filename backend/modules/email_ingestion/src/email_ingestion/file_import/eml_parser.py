import email
import email.policy
from pathlib import Path
from typing import List

from email_ingestion.models.email_document import EmailDocument
from email_ingestion.normalize import extract_email_document


def parse_eml(file_path: str) -> List[EmailDocument]:
    """Parses a single .eml file into a normalized EmailDocument.

    Returns a 1-element list for a uniform call signature with parse_mbox().
    """
    raw_bytes = Path(file_path).read_bytes()
    msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
    return [extract_email_document(msg, source="email")]
