from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseClusteringModel(ABC):
    name: str

    @abstractmethod
    def fit_predict(self, data: pd.DataFrame) -> list[int]:
        """
        Fit the clustering model on the provided data and return labels.
        """
        raise NotImplementedError
