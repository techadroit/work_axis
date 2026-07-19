from typing import List, Optional

from pydantic import BaseModel


class EmailDocument(BaseModel):
    """Normalized representation of a single email, regardless of source
    (Gmail API or a .mbox/.eml file import). This is the shared shape both
    ingestion paths produce, so downstream chunking/embedding code never
    needs to know where an email came from.
    """
    message_id: str
    thread_id: Optional[str] = None
    from_addr: str = ""
    to_addrs: List[str] = []
    subject: str = ""
    date: str = ""
    body_text: str = ""
    source: str = "email"
