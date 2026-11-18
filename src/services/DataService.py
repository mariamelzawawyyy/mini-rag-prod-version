from .BaseService import BaseService 
from .ProjectService import ProjectService 
from fastapi import UploadFile
from ..models.Enums import ResponseSignal  
import os
import re


# this service validates uploaded files types and size and if they are 
# compatible it will prepare the path where
# they will be stored  them in a file inside the project directory
# coming from projectservice 

class DataService(BaseService): 

    def __init__(self):
        super().__init__()
        self.size_scale = 1048576  # 1 MB in bytes

    def validate_uploaded_file(self, file: UploadFile):
        """Validate the uploaded file."""

        if file.content_type not in self.app_settings.file_allowed_types:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.file_max_size * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def generate_unique_filepath(self, original_filename: str, project_id: str,owner_id: str):
        random_key = self.generate_random_string()

        project_path = ProjectService().get_project_path(  
            project_id=project_id , 
            owner_id = owner_id
        )

        cleaned_filename = self.get_clean_filename(
            original_filename=original_filename
        )

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_filename
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_filename
            )

        return new_file_path, random_key

    def get_clean_filename(self, original_filename: str):
        cleaned_file_name = re.sub(
            r"[^\w.-]",
            "_",
            original_filename.strip()
        )

        return cleaned_file_name 
            



   