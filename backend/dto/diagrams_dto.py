from __future__ import annotations

from pydantic import BaseModel


class DiagramImageDTO(BaseModel):
    filename: str
    content_type: str
    data_base64: str


class DiagramsResponseDTO(BaseModel):
    upload_id: str
    diagram_type: str
    images: list[DiagramImageDTO]
