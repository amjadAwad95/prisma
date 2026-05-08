from __future__ import annotations

import pandas as pd
from sklearn.cluster import DBSCAN

from .base_clustering import BaseClusteringModel


class DBSCANClustering(BaseClusteringModel):
    name = "dbscan"

    def __init__(self, eps: float = 0.5, min_samples: int = 5) -> None:
        self.model = DBSCAN(eps=eps, min_samples=min_samples)

    def fit_predict(self, data: pd.DataFrame) -> list[int]:
        return self.model.fit_predict(data).tolist()
