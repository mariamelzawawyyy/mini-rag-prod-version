from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from src.helpers.config import get_settings, Settings
from src.Controllers import DataController, ProjectController, ProcessController
import aiofiles
from Models import ResponseSignal
import logging

# from .schemas.data import ProcessRequest

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)


@data_router.post("/upload/{project_id}")  # multi-tenant endpoint for uploading files
async def upload_file(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    """Upload a file for a specific project."""

    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        original_filename=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(
                app_settings.file_default_chunk_size
            ):
                await f.write(chunk)

    except Exception as e:
        logger.exception(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return JSONResponse(
        content={
            "message": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": file_id
        }
    )


# --------------------------------------------------
# PROCESS FILES - TEMPORARILY DISABLED
# --------------------------------------------------

# @data_router.post("/process/{project_id}")
# async def process_file(project_id: str, request: ProcessRequest):
#
#     file_id = request.file_id
#     chunk_size = request.chunk_size
#     overlap_size = request.overlap_size
#
#     process_controller = ProcessController(project_id=project_id)
#
#     file_content = process_controller.get_file_content(file_id=file_id)
#
#     file_chunks = process_controller.process_file_content(
#         file_content=file_content,
#         file_id=file_id,
#         chunk_size=chunk_size,
#         overlap_size=overlap_size
#     )
#
#     if file_chunks is None or len(file_chunks) == 0:
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"message": ResponseSignal.PROCESSING_FAILED.value}
#         )
#
#     return file_chunks 