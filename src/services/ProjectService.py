from .BaseService import BaseService
import os

# this service's only job is to get the project's directory on the disk
# and, if there isn't one, create it and pass the project directory
# to other services


class ProjectService(BaseService):

    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str, owner_id: str):

        base_dir = os.path.abspath(self.file_dir)
        #the base dir is the source of truth here where its the main
        # base_dir in the backend system and it will always be
        #/src/assets/files

        owner_dir = os.path.abspath(os.path.join(base_dir, owner_id))
        project_dir = os.path.abspath(os.path.join(owner_dir, project_id))
        # the path is now is  /src/assets/files/owner_id/project_id
        # but what if the user passed smething else rather than the project_id 
        # that will lead to another directory?

        #here comes comparing it with the source of truth 
        # if the parent directory of the owner is not the base dir,
        # or the parent directory of the project is not the owner dir
        # reject this process 
         
        if os.path.dirname(owner_dir) != base_dir:
            raise ValueError("Invalid owner id")

        if os.path.dirname(project_dir) != owner_dir:
            raise ValueError("Invalid project id")

        # project_dir = /src/assets/files/owner_id/project_id
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir 
  
         


