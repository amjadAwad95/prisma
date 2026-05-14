from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class ClusteringAlgorithm(str, Enum):
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    HIERARCHICAL = "hierarchical"


class ClusteringRunRequestDTO(BaseModel):
    upload_id: str
    algorithm: ClusteringAlgorithm


class ClusteringRunResponseDTO(BaseModel):
    output_file_path: str
    algorithm: ClusteringAlgorithm
    n_clusters: int
    noise_points: int | None = None
    insights: list[str] | None = None


class BestClusteringRunRequestDTO(BaseModel):
    upload_id: str


class ClusteringScoreDTO(BaseModel):
    algorithm: ClusteringAlgorithm
    silhouette: float
    n_clusters: int
    noise_points: int | None = None


class BestClusteringRunResponseDTO(BaseModel):
    output_file_path: str
    best_algorithm: ClusteringAlgorithm
    results: list[ClusteringScoreDTO]
    insights: list[str] | None = None
