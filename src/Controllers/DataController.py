from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from Models import ResponseSignal
import os
import re


class DataController(BaseController):

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

    def generate_unique_filepath(self, original_filename: str, project_id: str):
        random_key = self.generate_random_string()

        project_path = ProjectController().get_project_path(
            project_id=project_id
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
            



   