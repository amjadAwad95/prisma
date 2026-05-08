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
    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    output_path, labels = service.run(
        file_path=f"preprocessed/{file_record.filename}",
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
    )


@router.post("/best", response_model=BestClusteringRunResponseDTO)
def run_best_clustering(
    request: BestClusteringRunRequestDTO,
) -> BestClusteringRunResponseDTO:
    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    output_path, labels, algorithm, results = service.run_best(
        file_path=f"preprocessed/{file_record.filename}",
        upload_id=request.upload_id,
    )

    return BestClusteringRunResponseDTO(
        output_file_path=str(output_path),
        best_algorithm=algorithm,
        results=[ClusteringScoreDTO(**item) for item in results],
    )
