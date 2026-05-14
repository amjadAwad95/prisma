from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.time_series_service import TimeSeriesService
from dto.time_series_dto import (
    TimeSeriesRunRequestDTO,
    TimeSeriesRunResponseDTO,
)
from storage import FILE_DB

router = APIRouter(prefix="/time-series", tags=["time_series"])


@router.post("/run", response_model=TimeSeriesRunResponseDTO)
def run_time_series(request: TimeSeriesRunRequestDTO) -> TimeSeriesRunResponseDTO:
    """
    Run time series forecasting for an uploaded file.
    """

    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    service = TimeSeriesService()

    try:
        (
            transformed_data_file_path,
            forecast_file_path,
            historical_plot_path,
            forecast_plot_path,
            target_column,
            datetime_column,
            metrics,
            method_type,
        ) = service.run(
            f"uploads/{file_record.filename}",
            request.upload_id,
            request.method_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Time series run failed: {e}"
        ) from e

    return TimeSeriesRunResponseDTO(
        transformed_data_file_path=transformed_data_file_path,
        forecast_file_path=forecast_file_path,
        historical_plot_path=historical_plot_path,
        forecast_plot_path=forecast_plot_path,
        target_column=target_column,
        datetime_column=datetime_column,
        metrics=metrics,
        time_series_method_type=method_type,
    )
