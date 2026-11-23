from pydantic import BaseModel, Field
from typing import Optional
 
class ProcessRequest(BaseModel):
    file_id: Optional[str] = None 
    # the user will either pass the file id for the asset
    # he wants to be processed or wont pass and the logic will process all
    # the assets he has 
    chunk_size: int = 100
    overlap_size: int = 20 
    do_reset: bool = False  # if user chooses to reset , we will delete all chunks 
                            # and create them all over again 
    
    
 