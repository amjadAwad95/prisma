import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression

from .base_time_series import BaseTimeSeries


class LinearRegressionTimeSeries(BaseTimeSeries):
    """
    Linear Regression based forecasting.
    """

    def __init__(self, forecast_steps: int = 10):
        super().__init__(forecast_steps)

        self.model = LinearRegression()

    def run(
        self,
        data: pd.DataFrame,
        target_column: str,
    ):
        """Runs the linear regression forecasting algorithm.

        Args:
            data: DataFrame containing the time series data
            target_column: Name of the column to forecast

        Returns:
            forecast_df: DataFrame with forecasted values
            metrics: dict with evaluation metrics
        """
        values = data[target_column].values
        X = np.arange(len(values)).reshape(-1, 1)
        y = values
        self.model.fit(X, y)

        future_x = np.arange(
            len(values),
            len(values) + self.forecast_steps,
        ).reshape(-1, 1)

        predictions = self.model.predict(future_x)

        inferred_frequency = pd.infer_freq(data.index)

        if inferred_frequency is None:
            inferred_frequency = "D"

        future_dates = pd.date_range(
            start=data.index[-1],
            periods=self.forecast_steps + 1,
            freq=inferred_frequency,
        )[1:]

        forecast_df = pd.DataFrame(
            {
                "timestamp": future_dates,
                "forecast": predictions,
            }
        )

        metrics = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "trend": ("increasing" if values[-1] > values[0] else "decreasing"),
        }

        return forecast_df, metrics
