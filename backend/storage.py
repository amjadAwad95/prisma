from __future__ import annotations

from dto.upload_dto import UploadResponseDTO

# Simple in-memory store shared across routers in this process.
FILE_DB: dict[str, UploadResponseDTO] = {}
