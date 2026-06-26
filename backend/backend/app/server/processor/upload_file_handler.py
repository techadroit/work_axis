import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException

from backend.app.server.schemas.file_service_schema import UploadFileResponse
from core.utils.file_util import ALLOWED_MIME, EXT_BY_MIME, get_files_path
from backend.app.utils.logger_util import log_info, log_error


class UploadFileHandler:
    """
    A pipeline class for handling file uploads.
    Saves uploaded files to the data/files directory.
    """

    def __init__(self):
        """
        Initialize the UploadFilePipeline.

        Args:
            upload_dir: Directory where uploaded files will be saved (default: ../data/files)
        """
        self.upload_dir = get_files_path()
        self._ensure_upload_directory()

    def _ensure_upload_directory(self):
        """Create upload directory if it doesn't exist."""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            log_info(f"Upload directory ensured at: {self.upload_dir.absolute()}")
        except Exception as e:
            log_error(f"Failed to create upload directory: {str(e)}", exception=e)
            raise

    async def upload_file(self, file: UploadFile) -> UploadFileResponse:
        """
        Upload and save a file to the upload directory.

        Args:
            file: FastAPI UploadFile object

        Returns:
            dict: Contains filename, file_path, and upload status

        Raises:
            HTTPException: If upload fails
        """
        try:
            log_info(f"Starting file upload: {file.filename}")
            mime = (file.content_type or "").lower().strip()
            if mime not in ALLOWED_MIME:
                raise HTTPException(status_code=415, detail=f"Unsupported content-type: {mime or 'unknown'}")

            file_id = f"{uuid4().hex}"
            ext = EXT_BY_MIME.get(mime) or (mimetypes.guess_extension(mime) or ".bin")
            file_path = self.upload_dir / f"{file_id}{ext}"

            # Create file path
            # file_path = self.upload_dir / file.filename

            # Save file
            with file_path.open("wb") as buffer:
                content = await file.read()
                buffer.write(content)

            log_info(f"File uploaded successfully: {file_path}")

            # Extract file type/extension
            file_type = file_path.suffix.lstrip('.')

            return UploadFileResponse(
                file_name=file.filename,
                path=str(file_path),
                file_type=file_type,
                mime_type=mime,
            )
        except Exception as e:
            log_error(f"File upload failed: {str(e)}", exception=e)
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        finally:
            await file.close()

