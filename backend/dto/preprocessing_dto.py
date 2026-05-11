from __future__ import annotations

from pydantic import BaseModel
from enum import Enum


class MethodType(str, Enum):
    CLUSTERING = "clustering"
    ASSOCIATION_RULE = "association_rule"
    PCA = "pca"
    TIME_SERIES = "time_series"


class MethodTypeResponseDTO(BaseModel):
    method_type: list[MethodType]


class PreprocessingRunRequestDTO(BaseModel):
    upload_id: str
    method_type: MethodType


class PreprocessingRunResponseDTO(BaseModel):
    output_file_path: str
