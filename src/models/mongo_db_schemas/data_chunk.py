from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class DataChunk(BaseModel):

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: Optional[ObjectId] = Field(None, alias="_id")

    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)

    chunk_project_id: ObjectId = Field(
        ...,
        description="Reference to the associated project (projects._id)"
    )

    chunk_asset_id: ObjectId = Field(
        ...,
        description="Reference to the associated asset (assets._id)"
    )

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", 1)
                ],
                "unique": False,
                "name": "chunk_project_id_idx"
            } 
        ]
 
 
 
