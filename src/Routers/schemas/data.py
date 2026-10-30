# from pydantic import BaseModel, Field
# from typing import Optional
#
#
# class ProcessRequest(BaseModel):
#
#     file_id: str
#     chunk_size: Optional[int] = 100
#     overlap_size: Optional[int] = 20
#     do_reset: Optional[int] = 0
#
#     data: str = Field(..., description="The data to be processed.")
#     process_type: str = Field(..., description="The type of processing to be applied to the data.") 