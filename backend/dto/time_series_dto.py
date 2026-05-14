from enum import Enum

from pydantic import BaseModel


class TimeSeriesMethodType(str, Enum):
    LINEAR_REGRESSION = "linear_regression"
    ARIMA = "arima"


class TimeSeriesRunRequestDTO(BaseModel):
    upload_id: str
    method_type: TimeSeriesMethodType = TimeSeriesMethodType.LINEAR_REGRESSION


class TimeSeriesRunResponseDTO(BaseModel):
    transformed_data_file_path: str
    forecast_file_path: str
    historical_plot_path: str
    forecast_plot_path: str
    target_column: str
    datetime_column: str
    metrics: dict
    time_series_method_type: TimeSeriesMethodType
