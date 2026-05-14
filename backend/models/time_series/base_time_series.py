from abc import ABC, abstractmethod

import pandas as pd


class BaseTimeSeries(ABC):
    """
    Base class for time series forecasting models.
    """

    def __init__(self, forecast_steps: int = 10):
        self.forecast_steps = forecast_steps

    @abstractmethod
    def run(
        self,
        data: pd.DataFrame,
        target_column: str,
    ):
        """
        Runs the time series forecasting algorithm.

        Returns:
            forecast_df: DataFrame with forecasted values
            metrics: dict with evaluation metrics
        """
        pass
