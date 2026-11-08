from pydantic import BaseModel , Field , validator
from bson import ObjectId

class DataChunk(BaseModel):
    _id : Optional[ObjectId] 
    chunk_text : str = Field(... , min_length=1)
    chunk_metadata : dict  
    chunk_order : int = Field(... , gt=0)
    chunk_project_id : ObjectId = Field(... , description="Reference to the associated project") 