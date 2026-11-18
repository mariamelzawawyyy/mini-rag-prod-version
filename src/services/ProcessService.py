from .BaseService import BaseService
from .ProjectService import ProjectService
import os
import codecs
from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader
)
from ..models.Enums import ProcessingEnums
from langchain_text_splitters import RecursiveCharacterTextSplitter


# this service's responsibility is to take one uploaded file
# from a project's directory and do the splitting process
# to create chunks

class ProcessService(BaseService):

    def __init__(self, project_id: str, owner_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectService().get_project_path(
            project_id=project_id,
            owner_id=owner_id
        )

    # also apply here path traversal but for file not project
    def get_file_path(self, file_id: str) -> str:
        project_dir = os.path.abspath(self.project_path)
        file_path = os.path.abspath(os.path.join(project_dir, file_id))

        # reject ids like "../x" or "/etc/x" that would escape the project directory
        if os.path.dirname(file_path) != project_dir:
            raise ValueError("Invalid file id")

        return file_path

    def detect_file_type(self, file_path: str) -> str:
        # fallback used only when the file has no extension:
        # look at the first bytes of the content to guess the type
        with open(file_path, "rb") as f:
            header = f.read(2048)

        if header.startswith(b"%PDF-"):
            return ".pdf"

        # plain text: no null bytes and valid utf-8
        # (final=False so a multi-byte char cut at the 2048 boundary is not an error)
        if b"\x00" not in header:
            try:
                codecs.getincrementaldecoder("utf-8")().decode(header, final=False)
                return ".txt"
            except UnicodeDecodeError:
                pass

        return ""

    def get_file_extension(self, file_id: str):
        file_path = self.get_file_path(file_id=file_id)
        extension = os.path.splitext(file_path)[-1].lower()

        if not extension:
            extension = self.detect_file_type(file_path)

        return extension

    def get_file_loader(self, file_id: str):
        file_extension = self.get_file_extension(file_id=file_id)
        file_path = self.get_file_path(file_id=file_id)

        if file_extension == ProcessingEnums.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        elif file_extension == ProcessingEnums.PDF.value:
            return PyMuPDFLoader(file_path)

        else:
            raise ValueError(
                f"Unsupported file type: {file_extension or 'unknown'}"
            )

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)
        documents = loader.load()

        return documents

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        overlap_size: int = 20
    ):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len
        )

        file_content_texts = [
            record.page_content
            for record in file_content
        ]

        file_content_metadata = [
            record.metadata
            for record in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )

        return chunks 
              