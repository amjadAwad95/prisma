from fastapi import APIRouter, HTTPException

from services.pca_service import PCAService
from dto.pca_dto import PCARunRequestDTO, PCARunResponseDTO

from storage import FILE_DB

router = APIRouter(prefix="/pca", tags=["PCA"])


@router.post("/run", response_model=PCARunResponseDTO)
def run_pca(request: PCARunRequestDTO) -> PCARunResponseDTO:
    """
    Run PCA on the uploaded data.

    Args:
        request (PCARunRequestDTO): The request data containing upload ID and number of components.

    Returns:
        PCARunResponseDTO: The response containing the path to the PCA result file.
    """
    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    service = PCAService()
    output_path, pca_type, explained_variance_ratio, cumulative_variance = service.run(
        file_path=f"uploads/{file_record.filename}",
        upload_id=request.upload_id,
        n_components=request.n_components,
    )

    return PCARunResponseDTO(
        transformed_data_file_path=output_path,
        pca_method_type=pca_type,
        explained_variance_ratio=explained_variance_ratio,
        cumulative_variance=cumulative_variance,
    )
