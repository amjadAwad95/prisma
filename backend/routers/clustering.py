from __future__ import annotations

from fastapi import APIRouter, HTTPException

from dto.clustering_dto import (
    BestClusteringRunRequestDTO,
    BestClusteringRunResponseDTO,
    ClusteringAlgorithm,
    ClusteringRunRequestDTO,
    ClusteringRunResponseDTO,
    ClusteringScoreDTO,
)
from services.clustering_service import ClusteringService
from storage import FILE_DB

router = APIRouter(prefix="/clustering", tags=["clustering"])
service = ClusteringService()


@router.post("/run", response_model=ClusteringRunResponseDTO)
def run_clustering(request: ClusteringRunRequestDTO) -> ClusteringRunResponseDTO:
    """
    Run a clustering algorithm on the uploaded data.
    Args:
        request: ClusteringRunRequestDTO containing the upload ID and algorithm.
    Returns:
        ClusteringRunResponseDTO with the output file path, algorithm used, number of clusters, and noise points (if applicable).
    """
    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    output_path, labels, insights = service.run(
        file_path=f"uploads/{file_record.filename}",
        algorithm=request.algorithm,
        params={},
    )

    label_set = set(labels)
    noise_points = None
    if request.algorithm == ClusteringAlgorithm.DBSCAN:
        noise_points = labels.count(-1)
        label_set.discard(-1)

    n_clusters = len(label_set)

    return ClusteringRunResponseDTO(
        output_file_path=str(output_path),
        algorithm=request.algorithm,
        n_clusters=n_clusters,
        noise_points=noise_points,
        insights=insights,
    )


@router.post("/best", response_model=BestClusteringRunResponseDTO)
def run_best_clustering(
    request: BestClusteringRunRequestDTO,
) -> BestClusteringRunResponseDTO:
    """
    Run all the Clustering algorithms

    Args:
        request (BestClusteringRunRequestDTO): The id of the upload to run the algorithms on.

    Returns:
        BestClusteringRunResponseDTO: The best clustering results.
    """
    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    output_path, labels, algorithm, results, insights = service.run_best(
        file_path=f"uploads/{file_record.filename}",
        upload_id=request.upload_id,
    )

    return BestClusteringRunResponseDTO(
        output_file_path=str(output_path),
        best_algorithm=algorithm,
        results=[ClusteringScoreDTO(**item) for item in results],
        insights=insights,
    )
