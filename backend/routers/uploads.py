from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from dto.upload_dto import UploadResponseDTO
from storage import FILE_DB

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


def _safe_filename(original: str) -> str:
    """
    Sanitize the filename to prevent directory traversal and other issues.
    This function uses pathlib to extract just the filename, ignoring any path components.
    Args:
        original: The original filename from the upload.
    Returns:
        A sanitized filename that is safe to use on the filesystem.
    Raises:
        HTTPException: If the resulting filename is empty or invalid.
    """
    cleaned = Path(original).name
    if not cleaned:
        raise HTTPException(status_code=400, detail="Filename is required.")
    return cleaned


@router.post("/upload", response_model=UploadResponseDTO)
async def upload_data_file(file: UploadFile = File(...)) -> UploadResponseDTO:
    """
    Handle file uploads, saving them to disk and recording metadata in memory.
    Args:
        file: The uploaded file, provided as a form-data field.
    Returns:
        An UploadResponseDTO containing metadata about the uploaded file.
    Raises:
        HTTPException: If the file is missing, cannot be saved, or if the filename is
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")

    safe_name = _safe_filename(file.filename)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / safe_name

    try:
        content = await file.read()
        target_path.write_bytes(content)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Failed to save upload.") from exc

    upload_id = uuid4().hex
    record = UploadResponseDTO(
        upload_id=upload_id,
        filename=safe_name,
        content_type=file.content_type or "unknown",
        bytes=target_path.stat().st_size,
        path=str(target_path),
    )

    FILE_DB[upload_id] = record
    return record


@router.get("/metadata/{upload_id}", response_model=UploadResponseDTO)
async def get_file_metadata(upload_id: str) -> UploadResponseDTO:
    """
    Retrieve metadata for a specific uploaded file by its upload ID.
    Args:
        upload_id: The unique identifier for the uploaded file.
    Returns:
        An UploadResponseDTO containing metadata about the specified file.
    Raises:
        HTTPException: If no file metadata is found for the given upload ID.
    """
    record = FILE_DB.get(upload_id)
    if record is None:
        raise HTTPException(status_code=404, detail="File metadata not found.")
    return record


@router.get("/metadata", response_model=list[UploadResponseDTO])
async def list_file_metadata() -> list[UploadResponseDTO]:
    """
    Retrieve metadata for all uploaded files in the current session.
    Returns:
        A list of UploadResponseDTO objects, each containing metadata about an uploaded file.
    """
    return list(FILE_DB.values())
