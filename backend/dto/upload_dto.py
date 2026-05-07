from __future__ import annotations

from pydantic import BaseModel


class UploadResponseDTO(BaseModel):
    """
    Data Transfer Object for responses related to file uploads.
    Attributes:
        upload_id: A unique identifier for the uploaded file.
        filename: The original filename of the uploaded file.
        content_type: The MIME type of the uploaded file.
        bytes: The size of the uploaded file in bytes.
    """

    upload_id: str
    filename: str
    content_type: str
    bytes: int
    path: str
    method_types: list[str] | None = None
