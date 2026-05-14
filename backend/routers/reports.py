from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

from dto.report_dto import ReportRequestDTO, ReportResponseDTO
from models.agent.groq import GroqModel
from storage import FILE_DB
from utils.prompts import build_report_prompt
from utils.read_file import read_file

router = APIRouter(prefix="/reports", tags=["reports"])


def _serialize_value(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)


def _build_schema(df: pd.DataFrame) -> dict[str, Any]:
    columns: list[dict[str, Any]] = []
    for name in df.columns:
        series = df[name]
        example_values = (
            series.dropna().head(3).map(_serialize_value).tolist()
            if not series.dropna().empty
            else []
        )
        columns.append(
            {
                "name": name,
                "dtype": str(series.dtype),
                "missing": int(series.isna().sum()),
                "example_values": example_values,
            }
        )

    return {
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": columns,
    }


@router.post("/generate", response_model=ReportResponseDTO)
def generate_report(request: ReportRequestDTO) -> ReportResponseDTO:
    record = FILE_DB.get(request.upload_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Upload not found.")

    df = read_file(f"uploads/{record.filename}")
    schema = _build_schema(df)
    algorithms = [algo.model_dump() for algo in request.algorithms]

    prompt = build_report_prompt(df=df, schema=schema, algorithms=algorithms)
    model = GroqModel(config={"max_completion_tokens": 2500})
    report_text = model.generate(prompt)

    return ReportResponseDTO(
        upload_id=request.upload_id,
        report_text=report_text,
        schema=schema,
    )
