from pydantic import BaseModel


class AssociationRunRequestDTO(BaseModel):
    upload_id: str


class AssociationRunResponseDTO(BaseModel):
    frequent_itemsets_file_path: str
    association_rules_file_path: str
    min_support: float
    min_confidence: float
    min_lift: float
    insights: list[str] | None = None
