from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    file_name: str
    path: str
    file_type: str
    mime_type: str