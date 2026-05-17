from contextlib import asynccontextmanager
import os
from pathlib import Path
import shutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.uploads import router as uploads_router
from routers.preprocessing import router as preprocessing_router
from routers.clustering import router as clustering_router
from routers.association import router as association_router
from routers.pca import router as pca_router
from routers.time_series import router as time_series_router
from routers.reports import router as reports_router
from dto.upload_dto import UploadResponseDTO
from storage import FILE_DB


def _clear_directory(path: Path) -> None:
    if not path.exists():
        return

    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink(missing_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        _clear_directory(Path("uploads"))
        _clear_directory(Path("preprocessed"))
        _clear_directory(Path("clustered"))
        _clear_directory(Path("digrams"))
        _clear_directory(Path("association_results"))
        _clear_directory(Path("pca_output"))
        _clear_directory(Path("time_series_output"))
        FILE_DB.clear()


app = FastAPI(title="PRISMA API", lifespan=lifespan)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads_router)
app.include_router(preprocessing_router)
app.include_router(clustering_router)
app.include_router(association_router)
app.include_router(pca_router)
app.include_router(time_series_router)
app.include_router(reports_router)


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
