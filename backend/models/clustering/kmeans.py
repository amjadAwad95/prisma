from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans

from .base_clustering import BaseClusteringModel


class KMeansClustering(BaseClusteringModel):
    name = "kmeans"

    def __init__(self, n_clusters: int = 3, random_state: int = 42) -> None:
        self.model = KMeans(
            n_clusters=n_clusters,
            n_init="auto",
            random_state=random_state,
        )

    def fit_predict(self, data: pd.DataFrame) -> list[int]:
        """Fit the KMeans model to the data and return the cluster labels."""
        return self.model.fit_predict(data).tolist()
