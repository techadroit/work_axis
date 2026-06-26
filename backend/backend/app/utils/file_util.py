# Shim – re-exports from core so existing imports keep working unchanged.
from core.utils.file_util import (  # noqa: F401
    MIME_PDF,
    MIME_CSV,
    MIME_XLSX,
    MIME_XLS,
    MIME_DOCX,
    MIME_DOC,
    MIME_PPTX,
    MIME_PPT,
    IMAGE_MIME,
    ALLOWED_MIME,
    EXT_BY_MIME,
    get_install_root,
    get_data_path,
    get_files_path,
    get_vector_db_path,
    get_embedding_models_path,
)
