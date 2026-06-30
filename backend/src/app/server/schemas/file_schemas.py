from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class FileMeta(BaseModel):
    file_id: str
    orig_path: Path
    mime: str
    orig_filename: str
    # Optional preview artifact (e.g., thumbnail jpg or csv preview txt)
    preview_path: Optional[Path]
    preview_mime: Optional[str]