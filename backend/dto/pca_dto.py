from pydantic import BaseModel
from enum import Enum


class PCAMethodType(str, Enum):
    SVD = "SVD"
    COVARIANCE_MATRIX = "covariance_matrix"


class PCARunRequestDTO(BaseModel):
    upload_id: str
    n_components: float = None
    threshold: float = 0.95


class PCARunResponseDTO(BaseModel):
    transformed_data_file_path: str
    explained_variance_ratio: list
    cumulative_variance: list
    pca_method_type: PCAMethodType
