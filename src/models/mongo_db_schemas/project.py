from typing import Optional

from bson import ObjectId
# its a 12 byte bson data type used as the default unique identifier for 
# documents
from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,   
        populate_by_name=True)          

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)
    owner_id: str = Field(..., min_length=1) 


    # we cant write _id directly as it is stored in mongodb
    # note => mongo stores with every document it makes with  
    # a unique id by default (_id)
    # this id is different than the one we set by hand 


    # so if we write _id , pydantic will see that there is _ 
    #  pydantic considers  variables starting with _ as a private property 
    # cant be accessed or modified as pydantic ignores them  
    
    #the solution is to give it an alias by its real name _id
    # while naming it a fake name       