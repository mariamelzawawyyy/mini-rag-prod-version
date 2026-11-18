from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import aiofiles
import logging

from ..database.mongo import get_mongo_db
from ..helpers.config import get_settings, Settings
from ..services import DataService, ProcessService
from ..models.Enums import ResponseSignal
from ..models.ProjectModel import ProjectModel
from ..models.DataChunkModel import DataChunkModel
from ..models.mongo_db_schemas import DataChunk
from ..models.mini_rag_postgres.schemas.User import User
from ..dependencies import get_current_user
from .schemas.data import ProcessRequest
from ..services.ProjectService import ProjectService
  

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)
 

@data_router.post("/upload/{project_id}")  # multi-tenant endpoint for uploading files
async def upload_file(
    project_id: str,
    file: UploadFile,
    mongo_db=Depends(get_mongo_db),
    app_settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
):
    """Upload a file for a specific project."""

    owner_id = str(current_user.user_id)
    project_model = ProjectModel(db_client=mongo_db)
    
    #authorization part , if the user want to add a file to a specific project 
    # the project must exist and belong to him 
    project = await project_model.get_project(
        project_id = project_id , 
        owner_id = owner_id
    )
    if project is None:
          return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    data_service = DataService()
    is_valid, result_signal = data_service.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )

    project_dir_path = ProjectService().get_project_path(
        project_id=project_id,
        owner_id = owner_id )
     
    file_path, file_id = data_service.generate_unique_filepath(
        original_filename=file.filename,
        owner_id=owner_id, 
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


@data_router.post("/process/{project_id}")
async def process_file(
    project_id: str,
    process_request: ProcessRequest,
    mongo_db=Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    owner_id = str(current_user.user_id)

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = ProjectModel(db_client=mongo_db)

    # authorization: the project must exist AND belong to the current user
    project = await project_model.get_project( 
        project_id=project_id,
        owner_id=owner_id 
    )
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    chunk_model = DataChunkModel(db_client=mongo_db)

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    process_service = ProcessService(project_id=project_id,owner_id=owner_id)

    file_content = process_service.get_file_content(file_id=file_id)

    file_chunks = process_service.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.PROCESSING_FAILED.value}
        )

    # return file_chunks # 3yzeen b2a n7othom fl db (hnst3ml el datachunk model )
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id
        )
        for i, chunk in enumerate(file_chunks)
    ]

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    ) 