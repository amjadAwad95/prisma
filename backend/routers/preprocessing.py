from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from preprocessing.preprocessing import Preprocessing
from dto.preprocessing_dto import (
    MethodType,
    MethodTypeResponseDTO,
    PreprocessingRunResponseDTO,
    PreprocessingRunRequestDTO,
)
from models.groq import GroqModel
from storage import FILE_DB
from utils.read_file import read_file
from utils.prompts import build_get_method_type_prompt, get_prompt_for_method_type

router = APIRouter(prefix="/preprocessing", tags=["preprocessing"])


@router.get("/type/{upload_id}", response_model=MethodTypeResponseDTO)
def get_preprocessing_method_types(upload_id: str) -> list[MethodTypeResponseDTO]:
    """
    Get a list of available preprocessing method types.
    Args:
        upload_id: The unique identifier of the uploaded file for which to determine preprocessing methods.
    returns:
        A list of MethodTypeResponseDTO objects representing the supported preprocessing methods.
    """
    file_record = FILE_DB.get(upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    df = read_file(f"uploads/{file_record.filename}")

    prompt = build_get_method_type_prompt(df)

    groq = GroqModel()
    try:
        methods = groq.generate(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate method types: {e}"
        ) from e

    types = json.loads(methods)

    file_record.method_types = types["types"]

    method_list = [MethodType(type) for type in file_record.method_types]
    method_response_list = MethodTypeResponseDTO(method_type=method_list)

    return method_response_list


@router.post("/run")
def run_preprocessing(
    request: PreprocessingRunRequestDTO,
) -> PreprocessingRunResponseDTO:
    """
    Run the preprocessing code for a given uploaded file.
    Args:
        request: The request object containing the upload ID and method type.
    returns:
        A dictionary containing the status of the preprocessing operation.
    """

    file_record = FILE_DB.get(request.upload_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Upload not found.")

    if request.method_type not in file_record.method_types:
        raise HTTPException(
            status_code=400, detail="Invalid method type for this upload."
        )

    groq = GroqModel()

    preprocessor = Preprocessing()

    output_file = preprocessor.run(
        f"uploads/{file_record.filename}",
        get_prompt_for_method_type(request.method_type),
        groq,
    )

    return PreprocessingRunResponseDTO(output_file_path=str(output_file))
