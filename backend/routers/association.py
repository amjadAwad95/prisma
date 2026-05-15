from fastapi import APIRouter, HTTPException
from services.association_service import AssociationService
from dto.association_dto import AssociationRunRequestDTO, AssociationRunResponseDTO
from storage import FILE_DB

router = APIRouter(prefix="/association", tags=["Association Rule Mining"])


@router.post("/run", response_model=AssociationRunResponseDTO)
async def run_association_rule_mining(request: AssociationRunRequestDTO):
    """
    Run association rule mining on the uploaded data.

    Args:
        request (AssociationRunRequestDTO): The request data containing upload ID and thresholds.

    Returns:
        AssociationRunResponseDTO: The response containing paths to the results files.
    """
    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    service = AssociationService()
    itemsets_path, rules_path, thresholds, insights, rules_preview = service.run(
        file_path=f"uploads/{file_record.filename}",
    )
    return AssociationRunResponseDTO(
        frequent_itemsets_file_path=str(itemsets_path),
        association_rules_file_path=str(rules_path),
        min_support=thresholds["min_support"],
        min_confidence=thresholds["min_confidence"],
        min_lift=thresholds["min_lift"],
        insights=insights,
        rules=rules_preview,
    )
