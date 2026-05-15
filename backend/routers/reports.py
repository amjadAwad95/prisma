from __future__ import annotations

from typing import Any
from pathlib import Path
import json

import pandas as pd
from fastapi import APIRouter, HTTPException

from dto.report_dto import ReportRequestDTO, ReportResponseDTO
from models.agent.groq import GroqModel
from storage import FILE_DB
from prompts.report import build_report_prompt
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


def _load_insights(insights_path: Path) -> list[str] | None:
    if not insights_path.exists():
        return None

    try:
        payload = json.loads(insights_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    insights = payload.get("insights") if isinstance(payload, dict) else None
    if isinstance(insights, list) and all(isinstance(item, str) for item in insights):
        return insights

    return None


def _attach_insights(algorithms: list[dict[str, Any]], upload_id: str) -> None:
    for algo in algorithms:
        outputs = algo.get("outputs") or {}
        name = str(algo.get("name", "")).lower()

        if not name or name == "string":
            if "frequent_itemsets_file_path" in outputs:
                algo["name"] = "Association Rules"
            elif (
                "forecast_file_path" in outputs
                or "transformed_data_file_path" in outputs
            ):
                algo["name"] = "Time Series"
            elif "output_file_path" in outputs:
                algo["name"] = "Clustering"

        insights: list[str] | None = None

        output_path = outputs.get("output_file_path")
        if isinstance(output_path, str) and output_path.endswith(".csv"):
            insights_path = Path(output_path.replace(".csv", "_insights.json"))
            insights = _load_insights(insights_path)

        itemsets_path = outputs.get("frequent_itemsets_file_path")
        if insights is None and isinstance(itemsets_path, str):
            if itemsets_path.endswith("_itemsets.csv"):
                insights_path = Path(
                    itemsets_path.replace("_itemsets.csv", "_insights.json")
                )
            else:
                base_name = Path(itemsets_path).stem.replace("_itemsets", "")
                insights_path = (
                    Path("association_results")
                    / base_name
                    / f"{base_name}_insights.json"
                )
            insights = _load_insights(insights_path)

        if insights is None and (
            "time" in name
            or "forecast_file_path" in outputs
            or "transformed_data_file_path" in outputs
        ):
            insights_path = Path("time_series_output") / upload_id / "insights.json"
            insights = _load_insights(insights_path)

        outputs["insights"] = insights or ["Not provided"]
        if not algo.get("notes") and insights:
            algo["notes"] = " ".join(insights)
        algo["outputs"] = outputs


def _append_storage_insights(
    algorithms: list[dict[str, Any]],
    upload_id: str,
    filename: str,
) -> None:
    base_name = Path(filename).stem

    association_path = (
        Path("association_results") / base_name / f"{base_name}_insights.json"
    )
    association_insights = _load_insights(association_path)
    if association_insights:
        algorithms.append(
            {
                "name": "Association Rules",
                "outputs": {"insights": association_insights},
                "notes": " ".join(association_insights),
            }
        )

    time_series_path = Path("time_series_output") / upload_id / "insights.json"
    time_series_insights = _load_insights(time_series_path)
    if time_series_insights:
        algorithms.append(
            {
                "name": "Time Series",
                "outputs": {"insights": time_series_insights},
                "notes": " ".join(time_series_insights),
            }
        )

    clustered_dir = Path("clustered")
    if clustered_dir.exists():
        for insights_file in clustered_dir.glob(f"{base_name}_*_insights.json"):
            cluster_name = insights_file.stem.replace(f"{base_name}_", "")
            cluster_name = cluster_name.replace("_insights", "")
            cluster_insights = _load_insights(insights_file)
            if cluster_insights:
                algorithms.append(
                    {
                        "name": f"Clustering ({cluster_name})",
                        "outputs": {"insights": cluster_insights},
                        "notes": " ".join(cluster_insights),
                    }
                )


@router.post("/generate", response_model=ReportResponseDTO)
def generate_report(request: ReportRequestDTO) -> ReportResponseDTO:
    record = FILE_DB.get(request.upload_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Upload not found.")

    df = read_file(f"uploads/{record.filename}")
    schema = _build_schema(df)
    algorithms = [algo.model_dump() for algo in request.algorithms]

    _attach_insights(algorithms, request.upload_id)
    _append_storage_insights(algorithms, request.upload_id, record.filename)

    prompt = build_report_prompt(df=df, schema=schema, algorithms=algorithms)
    model = GroqModel(config={"max_completion_tokens": 2500})
    report_text = model.generate(prompt)

    return ReportResponseDTO(
        upload_id=request.upload_id,
        report_text=report_text,
        schema=schema,
    )
