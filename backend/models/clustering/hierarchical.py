from __future__ import annotations

import pandas as pd
from sklearn.cluster import AgglomerativeClustering

from .base_clustering import BaseClusteringModel


class HierarchicalClustering(BaseClusteringModel):
    name = "hierarchical"

    def __init__(self, n_clusters: int = 3, linkage: str = "ward") -> None:
        self.model = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage,
        )

    def fit_predict(self, data: pd.DataFrame) -> list[int]:
        return self.model.fit_predict(data).tolist()
