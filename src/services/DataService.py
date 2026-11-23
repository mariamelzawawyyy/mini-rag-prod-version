
from .BaseService import BaseService
from .ProjectService import ProjectService
from fastapi import UploadFile
from ..models.Enums import ResponseSignal
import os
import re


# This service validates uploaded files and prepares
# unique file paths inside the project directory.


class DataService(BaseService):

    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # 1 MB in bytes

    def validate_uploaded_file(self, file: UploadFile):
        """Validate the uploaded file type and size."""

        if file.content_type not in self.app_settings.file_allowed_types:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # file.size can be None if the size is unknown
        if (
            file.size is not None
            and file.size > self.app_settings.file_max_size * self.size_scale
        ):
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value

    def generate_unique_filepath(
        self,
        original_filename: str,
        project_id: str,
        owner_id: str
    ):
        """
        Generate a unique filename and its full path.

        The generated filename includes the original file extension.
        This filename will be used as the file_id throughout the application.
        """

        project_path = ProjectService().get_project_path(
            project_id=project_id,
            owner_id=owner_id
        )

        cleaned_filename = self.get_clean_filename(
            original_filename=original_filename
        )

        # Extract the original file extension
        file_extension = os.path.splitext(cleaned_filename)[1].lower()

        # Generate a unique filename
        random_key = self.generate_random_string()

        file_id = random_key + file_extension

        new_file_path = os.path.join(
            project_path,
            file_id
        )

        # Make sure the generated filename does not already exist
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            file_id = random_key + file_extension

            new_file_path = os.path.join(
                project_path,
                file_id
            )

        return new_file_path, file_id

    def get_clean_filename(self, original_filename: str):
        """Remove unsafe characters from the original filename."""

        # Normalize Windows path separators before extracting the filename
        original_filename = original_filename.replace("\\", "/")

        # Keep only the filename, not any directory path
        original_filename = os.path.basename(original_filename.strip())

        cleaned_filename = re.sub(
            r"[^\w.-]",
            "_",
            original_filename
        )

        return cleaned_filename
 
            



   