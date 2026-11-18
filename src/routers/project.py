from uuid import uuid4

from fastapi import APIRouter, Depends, Query, status

from ..database.mongo import get_mongo_db
from ..dependencies import get_current_user
from ..models.ProjectModel import ProjectModel
from ..models.mongo_db_schemas import Project
from ..models.mini_rag_postgres.schemas.User import User 
from ..services.ProjectService import ProjectService
 
project_router= APIRouter(    
    prefix="/api/v1/projects",   
    tags=["api_v1", "projects"]  
)

@project_router.post("/create_new_project", status_code=status.HTTP_201_CREATED)
async def create_new_project(
    mongo_db=Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    project_model = ProjectModel(db_client=mongo_db)
    project = await project_model.create_project(
        Project(
            project_id=str(uuid4()),
            owner_id=str(current_user.user_id),
        )
    )

    project_service = ProjectService()
    project_service.get_project_path(
        project_id=project.project_id,
        owner_id=project.owner_id,
    )

    return {"project_id": project.project_id} 

@project_router.get("/get_all_projects")
async def get_all_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10,ge=1,le=100),
    mongo_db=Depends(get_mongo_db),
    current_user: User = Depends(get_current_user) 
):
   project_model = ProjectModel(db_client=mongo_db) 
   projects , total_pages = await project_model.get_all_projects(
    owner_id = str(current_user.user_id),
    page = page ,
    page_size=page_size
   )
   return {
    "projects": [{"project_id": project.project_id} for project in projects],
    "page": page,
    "total_pages": total_pages,
} 



 
