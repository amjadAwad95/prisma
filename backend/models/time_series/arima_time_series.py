import numpy as np
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA

from .base_time_series import BaseTimeSeries


class ARIMATimeSeries(BaseTimeSeries):
    """
    ARIMA based forecasting.
    """

    def __init__(
        self,
        forecast_steps: int = 10,
        order: tuple[int, int, int] = (5,1,0),
    ):
        super().__init__(forecast_steps)
        self.order = order
        self.model = None
        self.model_fit = None

    def run(
        self,
        data: pd.DataFrame,
        target_column: str,
    ):
        """Runs the ARIMA forecasting algorithm.

        Args:
            data: DataFrame containing the time series data
            target_column: Name of the column to forecast

        Returns:
            forecast_df: DataFrame with forecasted values
            metrics: dict with evaluation metrics
        """
        values = data[target_column].values

        self.model = ARIMA(
            values,
            order=self.order,
        )

        self.model_fit = self.model.fit()

        predictions = self.model_fit.forecast(steps=self.forecast_steps)

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
            "aic": float(self.model_fit.aic),
            "bic": float(self.model_fit.bic),
        }

        return forecast_df, metrics
