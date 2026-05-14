import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from dto.time_series_dto import (
    TimeSeriesMethodType,
)
from models.agent.groq import GroqModel
from models.time_series.arima_time_series import (
    ARIMATimeSeries,
)
from models.time_series.linear_regression_time_series import (
    LinearRegressionTimeSeries,
)
from preprocessing.preprocessing import (
    Preprocessing,
)
from utils.prompts import (
    build_time_series_prompt,
)
from utils.read_file import read_file


class TimeSeriesService:
    """
    Service for time series analysis.
    """
    FORECAST_STEPS = 10
    ARIMA_ORDER = (5, 1, 0)

    def __init__(self):
        self.processor = Preprocessing()

        self.model = GroqModel()

    def run(
        self,
        file_path: str,
        upload_id: str,
        method_type: TimeSeriesMethodType,
    ):
        """runs time series forecasting.

        Args:
            file_path: path to the uploaded file
            upload_id: unique identifier for the upload session
            method_type: type of forecasting method to use (linear regression or ARIMA)

        Returns:
            tuple containing paths to the transformed data, forecast output, historical plot, forecast plot, target column name, datetime column name, evaluation metrics, and the method type used
        """
        prompt_fun = build_time_series_prompt

        preprocessed_path = self.processor.run(
            file_path=file_path,
            prompt_fun=prompt_fun,
            model=self.model,
        )

        preprocessed_df = read_file(str(preprocessed_path))

        datetime_column = self._detect_datetime_column(preprocessed_df)

        preprocessed_df[datetime_column] = pd.to_datetime(
            preprocessed_df[datetime_column],
            errors="coerce",
        )

        preprocessed_df = preprocessed_df.dropna(subset=[datetime_column])

        preprocessed_df = preprocessed_df.sort_values(datetime_column)

        preprocessed_df = preprocessed_df.set_index(datetime_column)

        target_column = self._detect_target_column(preprocessed_df)

        preprocessed_df[target_column] = (
            preprocessed_df[target_column].interpolate(method="linear").ffill().bfill()
        )

        ts_model = self._build_model(method_type)

        forecast_df, metrics = ts_model.run(
            data=preprocessed_df,
            target_column=target_column,
        )

        output_dir = Path("time_series_output") / upload_id

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        transformed_data_path = output_dir / "preprocessed_time_series.csv"

        forecast_output_path = output_dir / "forecast.csv"

        metrics_output_path = output_dir / "metrics.json"

        historical_plot_path = output_dir / "historical_plot.png"

        forecast_plot_path = output_dir / "forecast_plot.png"

        preprocessed_df.to_csv(transformed_data_path)

        forecast_df.to_csv(
            forecast_output_path,
            index=False,
        )

        metrics_output_path.write_text(
            json.dumps(metrics),
            encoding="utf-8",
        )

        self._save_diagrams(
            historical_df=preprocessed_df,
            forecast_df=forecast_df,
            target_column=target_column,
            historical_plot_path=historical_plot_path,
            forecast_plot_path=forecast_plot_path,
        )

        return (
            str(transformed_data_path),
            str(forecast_output_path),
            str(historical_plot_path),
            str(forecast_plot_path),
            target_column,
            datetime_column,
            metrics,
            method_type,
        )

    def _build_model(
        self,
        method_type: TimeSeriesMethodType,
    ):
        """_builds the time series forecasting model based on the specified method type.

        Args:
            method_type: type of forecasting method to use (linear regression or ARIMA)

        Raises:
            ValueError: if an unsupported method type is provided

        Returns:
            An instance of the time series forecasting model corresponding to the specified method type
        """
        if method_type == TimeSeriesMethodType.LINEAR_REGRESSION:
            return LinearRegressionTimeSeries(forecast_steps=self.FORECAST_STEPS)

        if method_type == TimeSeriesMethodType.ARIMA:
            return ARIMATimeSeries(
                forecast_steps=self.FORECAST_STEPS,
                order=self.ARIMA_ORDER,
            )

        raise ValueError(f"Unsupported method: {method_type}")

    def _detect_datetime_column(
        self,
        df: pd.DataFrame,
    ) -> str:
        """_detects the datetime column in the given DataFrame.

        Args:
            df: DataFrame to analyze for datetime column

        Raises:
            ValueError: if no datetime column is found in the DataFrame

        Returns:
            The name of the detected datetime column in the DataFrame
        """
        for column in df.columns:
            try:
                parsed = pd.to_datetime(
                    df[column],
                    errors="raise",
                )

                if parsed.notna().sum() > 0:
                    return column

            except Exception:
                continue

        raise ValueError("No datetime column found")

    def _detect_target_column(
        self,
        df: pd.DataFrame,
    ) -> str:
        """_detects the target column in the given DataFrame.

        Args:
            df: DataFrame to analyze for the target column

        Raises:
            ValueError: if no numeric column is found in the DataFrame

        Returns:
            The name of the detected target column in the DataFrame
        """
        numeric_columns = df.select_dtypes(include="number").columns

        if len(numeric_columns) == 0:
            raise ValueError("No numeric columns found")

        return numeric_columns[0]

    def _save_diagrams(
        self,
        historical_df: pd.DataFrame,
        forecast_df: pd.DataFrame,
        target_column: str,
        historical_plot_path: Path,
        forecast_plot_path: Path,
    ) -> None:
        """_saves the historical and forecast plots for the time series data.

        Args:
            historical_df: DataFrame containing the historical time series data
            forecast_df: DataFrame containing the forecasted time series data
            target_column: Name of the target column in the DataFrames
            historical_plot_path: Path to save the historical plot image
            forecast_plot_path: Path to save the forecast plot image
        """
        plt.figure(figsize=(10, 6))
        plt.plot(
            historical_df.index,
            historical_df[target_column],
        )
        plt.title("Historical Time Series")
        plt.xlabel("Time")
        plt.ylabel(target_column)
        plt.tight_layout()
        plt.savefig(
            historical_plot_path,
            dpi=160,
        )
        plt.close()
        plt.figure(figsize=(10, 6))
        plt.plot(
            historical_df.index,
            historical_df[target_column],
            label="Historical",
        )
        plt.plot(
            forecast_df["timestamp"],
            forecast_df["forecast"],
            label="Forecast",
        )
        plt.title("Forecast Visualization")
        plt.xlabel("Time")
        plt.ylabel(target_column)
        plt.legend()
        plt.tight_layout()
        plt.savefig(
            forecast_plot_path,
            dpi=160,
        )

        plt.close()
