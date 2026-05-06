from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from routers.uploads import router as uploads_router
from routers.preprocessing import router as preprocessing_router
from dto.upload_dto import UploadResponseDTO
from storage import FILE_DB


def _clear_directory(path: Path) -> None:
    if not path.exists():
        return

    for item in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            item.rmdir()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        _clear_directory(Path("uploads"))
        _clear_directory(Path("preprocessed"))
        FILE_DB.clear()


app = FastAPI(title="SmartAnalyticsApp API", lifespan=lifespan)

app.include_router(uploads_router)
app.include_router(preprocessing_router)


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
