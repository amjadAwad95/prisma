from fastapi import FastAPI

from routers.uploads import router as uploads_router
from dto.upload_dto import UploadResponseDTO
from storage import FILE_DB

app = FastAPI(title="SmartAnalyticsApp API")

app.include_router(uploads_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Root endpoint to verify the API is running.
    returns:
        A simple status message.
    """
    return {"status": "ok"}


@app.get("/session", response_model=dict[str, UploadResponseDTO])
def get_session_summary() -> dict[str, UploadResponseDTO]:
    """
    Get a summary of the current session, including all uploaded files.
    returns:
        A dictionary mapping upload IDs to their metadata.
    """
    return FILE_DB


def get_session_summary() -> dict[str, UploadResponseDTO]:
    """
    Get a summary of the current session, including all uploaded files.
    returns:
        A dictionary mapping upload IDs to their metadata.
    """
    return FILE_DB
