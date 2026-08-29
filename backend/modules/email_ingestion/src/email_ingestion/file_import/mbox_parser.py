import email
import email.policy
import mailbox
from typing import List

from email_ingestion.models.email_document import EmailDocument
from email_ingestion.normalize import extract_email_document


def _modern_message_factory(fp):
    # mailbox.mbox defaults to the legacy compat32 Message API, which lacks
    # get_content()/is_multipart() walking used by normalize.py. Force the
    # modern policy.default (EmailMessage) parser instead.
    return email.message_from_binary_file(fp, policy=email.policy.default)


def parse_mbox(file_path: str) -> List[EmailDocument]:
    """Parses a .mbox file into a list of normalized EmailDocuments."""
    box = mailbox.mbox(file_path, factory=_modern_message_factory)
    documents = []
    for msg in box:
        documents.append(extract_email_document(msg, source="email"))
    return documents
