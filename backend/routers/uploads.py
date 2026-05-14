from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from dto.diagrams_dto import DiagramImageDTO, DiagramsResponseDTO
from dto.upload_dto import UploadResponseDTO
from storage import FILE_DB

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
DIGRAMS_DIR = Path("digrams")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


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

    _safe_filename(file.filename)
    upload_id = uuid4().hex
    stored_name = f"{upload_id}_{file.filename}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / stored_name

    try:
        content = await file.read()
        target_path.write_bytes(content)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Failed to save upload.") from exc

    record = UploadResponseDTO(
        upload_id=upload_id,
        filename=stored_name,
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


@router.get("/diagrams/{upload_id}/{diagram_type}", response_model=DiagramsResponseDTO)
async def list_diagrams(upload_id: str, diagram_type: str) -> DiagramsResponseDTO:
    """
    Retrieve diagram images for a specific upload ID and diagram type.
    """
    record = FILE_DB.get(upload_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Upload not found.")

    category_dir = DIGRAMS_DIR / upload_id / diagram_type
    if not category_dir.exists():
        raise HTTPException(status_code=404, detail="Diagrams not found.")

    images: list[DiagramImageDTO] = []
    for path in sorted(category_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            content_type, _ = mimetypes.guess_type(path.name)
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            images.append(
                DiagramImageDTO(
                    filename=path.name,
                    content_type=content_type or "application/octet-stream",
                    data_base64=encoded,
                )
            )

    return DiagramsResponseDTO(
        upload_id=upload_id,
        diagram_type=diagram_type,
        images=images,
    )
