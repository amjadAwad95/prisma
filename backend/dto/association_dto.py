from pydantic import BaseModel

class AssociationRunRequestDTO(BaseModel):
    upload_id: str
    min_support: float
    min_confidence: float
    min_lift: float
    
class AssociationRunResponseDTO(BaseModel):
    frequent_itemsets_file_path: str
    association_rules_file_path: str