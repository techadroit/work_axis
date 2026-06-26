import os
import sys
from pathlib import Path


MIME_PDF = "application/pdf"
MIME_CSV = "text/csv"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME_XLS = "application/vnd.ms-excel"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_DOC = "application/msword"
# PowerPoint
MIME_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
MIME_PPT = "application/vnd.ms-powerpoint"

IMAGE_MIME = {"image/jpeg", "image/png", "image/webp"}

ALLOWED_MIME = set(IMAGE_MIME) | {
    MIME_PDF,
    MIME_CSV,
    MIME_XLSX,
    MIME_XLS,
    MIME_DOCX,
    MIME_DOC,
    MIME_PPTX,
    MIME_PPT,
}

EXT_BY_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    MIME_PDF: ".pdf",
    MIME_CSV: ".csv",
    MIME_XLSX: ".xlsx",
    MIME_XLS: ".xls",
    MIME_DOCX: ".docx",
    MIME_DOC: ".doc",
    MIME_PPTX: ".pptx",
    MIME_PPT: ".ppt",
}


def get_install_root(start: Path | str = None, markers=(".git", "pyproject.toml", "setup.cfg"), env_var: str = "APP_INSTALL_DIR") -> Path:
    """
    Return the installation / project root directory.

    Resolution order:
      1. APP_INSTALL_DIR environment variable (if set)
      2. first parent of `start` (or this file) that contains any marker file/folder
      3. current working directory

    Usage:
      root = get_install_root()
      db_path = root / "data" / "db" / "app_checkpoints.db"
    """
    # 1) env override
    env_path = os.environ.get(env_var)
    if env_path:
        return Path(env_path).expanduser().resolve()

    # 2) PyInstaller bundled executable
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent

    # 3) walk parents looking for marker files (development mode)
    start_path = Path(start).resolve() if start else Path.cwd()
    for p in [start_path, *start_path.parents]:
        if any((p / m).exists() for m in markers):
            return p

    # 4) fallback
    return Path.cwd()


def get_data_path() -> Path:
    """Get the data directory path."""
    return get_install_root() / "data"


def get_files_path() -> Path:
    """Get the files directory path."""
    return get_data_path() / "files"


def get_vector_db_path() -> Path:
    """Get the vector database directory path."""
    return get_data_path() / "vector_database"


def get_embedding_models_path() -> Path:
    """Get the embedding models directory path."""
    return get_data_path() / "embedding_models"
