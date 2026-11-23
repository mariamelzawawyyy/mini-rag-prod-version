
import os
import logging

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse

from ..database.mongo import get_mongo_db
from ..dependencies import get_current_user
from ..helpers.config import get_settings, Settings
from ..services import DataService, ProcessService
from ..models.Enums import ResponseSignal, AssetTypeEnums
from ..models.ProjectModel import ProjectModel
from ..models.DataChunkModel import DataChunkModel
from ..models.AssetModel import AssetModel
from ..models.mongo_db_schemas import DataChunk, Asset
from ..models.mini_rag_postgres.schemas.User import User
from .schemas.data import ProcessRequest

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    mongo_db=Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
    app_settings: Settings = Depends(get_settings),
):
    owner_id = str(current_user.user_id)

    project_model = await ProjectModel.create_instance(db_client=mongo_db)
    project = await project_model.get_project(project_id=project_id, owner_id=owner_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    data_service = DataService()
    is_valid, result_signal = data_service.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    file_path, file_id = data_service.generate_unique_filepath(
        original_filename=file.filename,
        project_id=project_id,
        owner_id=owner_id,
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.file_default_chunk_size):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value},
        )

    try:
        asset_model = await AssetModel.create_instance(db_client=mongo_db)

        asset_resource = Asset(
            asset_project_id=project.id,
            asset_type=AssetTypeEnums.FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path),
        )

        asset_record = await asset_model.create_asset(asset=asset_resource)

    except Exception as e:
        logger.error(f"Error while saving asset record: {e}")

        if os.path.exists(file_path):
            os.remove(file_path)

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            },
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": asset_record.asset_name,
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
    project_id: str,
    process_request: ProcessRequest,
    mongo_db=Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    owner_id = str(current_user.user_id)

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=mongo_db)
    project = await project_model.get_project(project_id=project_id, owner_id=owner_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    asset_model = await AssetModel.create_instance(db_client=mongo_db)

    project_files_ids = {}

    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            file_id=process_request.file_id,
        )
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": ResponseSignal.NO_ASSETS_FOUND.value},
            )
        project_files_ids = {asset_record.id: asset_record.asset_name}
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnums.FILE.value,
        )
        project_files_ids = {record.id: record.asset_name for record in project_files}

    if not project_files_ids:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.NO_ASSETS_FOUND.value},
        )

    process_service = ProcessService(project_id=project_id, owner_id=owner_id)
    chunk_model = await DataChunkModel.create_instance(db_client=mongo_db)

    # prepare new chunks before deleting old ones
    all_chunks_records = []
    no_files = 0

    for asset_mongo_id, file_id in project_files_ids.items():
        file_content = process_service.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            )

        file_chunks = process_service.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )
        if not file_chunks:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            )

        all_chunks_records.extend(
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_mongo_id,
            )
            for i, chunk in enumerate(file_chunks)
        )
        no_files += 1

    # delete old chunks only when reset is requested
    if do_reset:
        if process_request.file_id:
            await chunk_model.delete_chunks_by_asset_id(
                project_id=project.id,
                asset_id=asset_record.id,
            )
        else:
            await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    no_records = await chunk_model.insert_many_chunks(chunks=all_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files,
        }
    )
 
 



 




 
 