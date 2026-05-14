from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AlgorithmReportInputDTO(BaseModel):
    name: str
    measures: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    outputs: dict[str, Any] | None = None
    notes: str | None = None


class ReportRequestDTO(BaseModel):
    upload_id: str
    algorithms: list[AlgorithmReportInputDTO]


class ReportResponseDTO(BaseModel):
    upload_id: str
    report_text: str
    schema: dict[str, Any]
