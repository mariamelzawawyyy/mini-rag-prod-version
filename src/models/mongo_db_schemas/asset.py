from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


# named "asset" and not "file" because later it can be a url or anything else
class Asset(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: Optional[ObjectId] = Field(None, alias="_id")  # mongo _id
    asset_project_id: ObjectId  # reference to projects._id
    asset_type: str = Field(..., min_length=1)  # a file or anything else
    asset_name : str = Field(..., min_length=1) # the name of the file or asset 
                                                # that we stored the file_id in the backend  
    asset_size: Optional[int] = Field(default=None, ge=0)
    asset_config: Optional[dict] = Field(default=None)
    asset_pushed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_project_id", 1), ("asset_name", 1)],  
                "unique": True,
                "name": "asset_project_id_asset_name_uidx",  
            }
        ] 

