import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from models.agent.groq import GroqModel
from models.time_series.arima_time_series import ARIMATimeSeries
from preprocessing.preprocessing import Preprocessing
from prompts.time_series import (
    build_time_series_insights_prompt,
    build_time_series_prompt,
)
from utils.read_file import read_file


class TimeSeriesService:
    """Service for time series analysis."""

    FORECAST_STEPS = 10
    ARIMA_ORDER = (5, 1, 0)

    def __init__(self):
        self.processor = Preprocessing()
        self.model = GroqModel()

    def run(self, file_path: str, upload_id: str):
        """Run time series forecasting using ARIMA only.

        Args:
            file_path: path to the uploaded file
            upload_id: unique identifier for the upload session

        Returns:
            Tuple containing the transformed data path, forecast path,
            historical plot path, forecast plot path, target column name,
            datetime column name, metrics, and method name.
        """
        preprocessed_path = self.processor.run(
            file_path=file_path,
            prompt_fun=build_time_series_prompt,
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

        method_name = "arima"
        ts_model = self._build_model()

        forecast_df, metrics = ts_model.run(
            data=preprocessed_df,
            target_column=target_column,
        )

        output_dir = Path("time_series_output") / upload_id
        diagrams_path = Path("digrams") / upload_id / "time_series"
        output_dir.mkdir(parents=True, exist_ok=True)
        diagrams_path.mkdir(parents=True, exist_ok=True)

        transformed_data_path = output_dir / "transformed_time_series.csv"
        forecast_output_path = output_dir / "forecast.csv"
        metrics_output_path = output_dir / "metrics.json"
        insights_output_path = output_dir / "insights.json"
        historical_plot_path = diagrams_path / "historical_plot.png"
        forecast_plot_path = diagrams_path / "forecast_plot.png"

        preprocessed_df.to_csv(transformed_data_path)
        forecast_df.to_csv(forecast_output_path, index=False)

        insights = self._build_time_series_insights(
            preprocessed_df[target_column],
            forecast_df,
            method_name,
        )
        metrics["insights"] = insights

        metrics_output_path.write_text(json.dumps(metrics), encoding="utf-8")
        insights_output_path.write_text(
            json.dumps({"insights": insights}),
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
            method_name,
        )

    def _build_model(self, forecast_steps: int | None = None):
        """Build the ARIMA model used for forecasting.

        Args:
            forecast_steps: optional number of forecast steps to generate

        Returns:
            An ARIMATimeSeries instance configured with service defaults.
        """
        steps = forecast_steps or self.FORECAST_STEPS
        return ARIMATimeSeries(
            forecast_steps=steps,
            order=self.ARIMA_ORDER,
        )

    def _backtest_method(
        self,
        df: pd.DataFrame,
        target_column: str,
        holdout: int,
    ) -> float | None:
        """Backtest the ARIMA model using a holdout window.

        Args:
            df: DataFrame indexed by datetime containing the target column
            target_column: name of the target column to forecast
            holdout: number of rows to reserve for testing

        Returns:
            Mean absolute error over the holdout window, or None if backtest fails.
        """
        train_df = df.iloc[:-holdout]
        test_df = df.iloc[-holdout:]

        if train_df.empty or test_df.empty:
            return None

        try:
            model = self._build_model(forecast_steps=holdout)
            forecast_df, _ = model.run(
                data=train_df,
                target_column=target_column,
            )
            predictions = forecast_df["forecast"].to_numpy()
            actual = test_df[target_column].to_numpy()
            limit = min(len(predictions), len(actual))
            if limit == 0:
                return None
            return float(np.mean(np.abs(actual[:limit] - predictions[:limit])))
        except Exception:
            return None

    def _build_time_series_insights(
        self,
        history: pd.Series,
        forecast_df: pd.DataFrame,
        method_name: str,
    ) -> list[str]:
        """Build human-readable insights from history and forecast data.

        Args:
            history: historical series indexed by datetime
            forecast_df: forecast output DataFrame
            method_name: forecasting method used

        Returns:
            A list of insight strings, either from the LLM or a fallback formatter.
        """
        facts = self._build_time_series_facts(history, forecast_df, method_name)
        if not facts:
            return []

        llm_output = self._summarize_time_series_facts_with_llm(facts)
        if llm_output:
            return llm_output

        return self._format_time_series_facts(facts)

    def _build_time_series_facts(
        self,
        history: pd.Series,
        forecast_df: pd.DataFrame,
        method_name: str,
    ) -> dict[str, object] | None:
        """Build a structured facts payload for insight generation.

        Args:
            history: historical series indexed by datetime
            forecast_df: forecast output DataFrame
            method_name: forecasting method used

        Returns:
            A facts dictionary, or None if the input data is missing.
        """
        if history is None or history.empty or forecast_df is None or forecast_df.empty:
            return None

        first_value = float(history.iloc[0])
        last_value = float(history.iloc[-1])
        recent_window = history.iloc[-min(5, len(history)) :]
        recent_change = float(recent_window.iloc[-1] - recent_window.iloc[0])

        forecast_series = forecast_df["forecast"]
        forecast_end = float(forecast_series.iloc[-1])
        forecast_change = float(forecast_end - last_value)

        forecast_points: list[dict[str, object]] = []
        for _, row in forecast_df.head(5).iterrows():
            timestamp = row.get("timestamp")
            if pd.isna(timestamp):
                continue
            forecast_points.append(
                {
                    "timestamp": str(pd.to_datetime(timestamp)),
                    "value": round(float(row.get("forecast", 0.0)), 2),
                }
            )

        def _direction(value: float) -> str:
            if value > 0:
                return "up"
            if value < 0:
                return "down"
            return "flat"

        return {
            "summary": "Time series insights for the latest data.",
            "history_direction": _direction(last_value - first_value),
            "recent_direction": _direction(recent_change),
            "forecast_direction": _direction(forecast_change),
            "method": method_name,
            "forecast_points": forecast_points,
        }

    def _format_time_series_facts(self, facts: dict[str, object]) -> list[str]:
        """Format the facts payload into readable insight strings.

        Args:
            facts: facts dictionary produced by `_build_time_series_facts`

        Returns:
            A list of formatted insight strings.
        """
        summary = facts.get("summary")
        insights: list[str] = [str(summary)] if summary else []

        history_direction = facts.get("history_direction")
        recent_direction = facts.get("recent_direction")
        forecast_direction = facts.get("forecast_direction")
        forecast_points = facts.get("forecast_points", [])

        if history_direction and history_direction != "flat":
            insights.append(f"Overall, the trend has been moving {history_direction}.")
        elif history_direction:
            insights.append("Overall, the trend has been mostly flat.")

        if recent_direction and recent_direction != "flat":
            insights.append(f"Recent values are moving {recent_direction}.")
        elif recent_direction:
            insights.append("Recent values are steady.")

        if forecast_direction and forecast_direction != "flat":
            insights.append(
                f"The forecast suggests it may move {forecast_direction} next."
            )
        elif forecast_direction:
            insights.append("The forecast suggests a stable outlook next.")

        if isinstance(forecast_points, list) and forecast_points:
            point_lines = ", ".join(
                [f"{item['timestamp']}: {item['value']}" for item in forecast_points]
            )
            insights.append(f"Next points: {point_lines}.")

        return insights

    def _summarize_time_series_facts_with_llm(
        self,
        facts: dict[str, object],
    ) -> list[str] | None:
        """Summarize the facts payload with an LLM.

        Args:
            facts: facts dictionary to summarize

        Returns:
            A list of LLM-generated insight strings, or None if parsing fails.
        """
        prompt = build_time_series_insights_prompt(facts)

        try:
            model = GroqModel(config={"max_completion_tokens": 600})
            output = model.generate(prompt)
            parsed = json.loads(output)
            if isinstance(parsed, list) and all(
                isinstance(item, str) for item in parsed
            ):
                return parsed
        except (json.JSONDecodeError, ValueError, TypeError):
            return None

        return None

    def _detect_datetime_column(self, df: pd.DataFrame) -> str:
        """Detect the datetime column in the input DataFrame.

        Args:
            df: DataFrame to analyze for a datetime column

        Raises:
            ValueError: if no datetime column is found

        Returns:
            The name of the detected datetime column.
        """
        for column in df.columns:
            try:
                parsed = pd.to_datetime(df[column], errors="raise")
                if parsed.notna().sum() > 0:
                    return column
            except Exception:
                continue

        raise ValueError("No datetime column found")

    def _detect_target_column(self, df: pd.DataFrame) -> str:
        """Detect the first numeric column to use as the target.

        Args:
            df: DataFrame to analyze for the target column

        Raises:
            ValueError: if no numeric column is found

        Returns:
            The name of the detected target column.
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
        """Save the historical and forecast plot images.

        Args:
            historical_df: DataFrame containing the historical series
            forecast_df: DataFrame containing the forecasted series
            target_column: name of the target column
            historical_plot_path: path to save the historical plot image
            forecast_plot_path: path to save the forecast plot image
        """
        plt.figure(figsize=(10, 6))
        plt.plot(
            historical_df.index, historical_df[target_column], marker="o", linewidth=2
        )
        plt.title("Historical Time Series")
        plt.xlabel("Time")
        plt.ylabel(target_column)
        plt.tight_layout()
        plt.savefig(historical_plot_path, dpi=160)
        plt.close()

        plt.figure(figsize=(10, 6))
        plt.plot(
            historical_df.index,
            historical_df[target_column],
            label="Historical",
            marker="o",
            linewidth=2,
        )
        plt.plot(
            forecast_df["timestamp"],
            forecast_df["forecast"],
            label="Forecast",
            marker="o",
            linewidth=2,
        )
        plt.title("Forecast Visualization")
        plt.xlabel("Time")
        plt.ylabel(target_column)
        plt.legend()
        plt.tight_layout()
        plt.savefig(forecast_plot_path, dpi=160)
        plt.close()
