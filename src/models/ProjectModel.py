from .BaseDataModel import BaseDataModel 
from .mongo_db_schemas import Project
from .Enums import DbEnums

# the code responsible for dealing with projects collection in mongodb
class ProjectModel(BaseDataModel):  
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DbEnums.COLLECTION_PROJECT_NAME.value] 
        #the projects collection

    @classmethod
    async def create_instance(cls,db_client:object) :
        instance = cls(db_client)   
        # this is equivalent to creating an object from 
        # the projectmodel class  
        # just like saying project_object = ProjectModel(db_client) 
        # so it will automatically have both db client and collection 
        # next tie we want to create an object we dont just use 
        # project_model = ProjectModel(db_client=mongo_db)  
        # it will be
        #project_model = ProjectModel.create_instance  
        await instance.init_collection()  
        # this is equivalent to creating an instance from
        # the object we created before 
        # this is like projectObject.init_collection() 
        return instance 

    async def init_collection(self):
        for index in Project.get_indexes():
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"],
            ) 
    # this gets the indexes we defined in the project schema and
    #actually creates them for this specific collection             
    
    async def create_project(self, project:Project):     
        result = await self.collection.insert_one(project.model_dump(
            by_alias = True ,
            exclude_none = True #or  exclude_unset = true (look for it later)
        ))  
        project.id = result.inserted_id
        return project 


    async def get_project(self, project_id:str,owner_id:str):       
        record = await self.collection.find_one({"project_id": project_id ,"owner_id": owner_id })   
        if record is None:  
            return None 
            
        return Project(**record)    
             
        
    async def get_all_projects(self,owner_id:str, page:int = 1 , page_size:int = 10):
        #get all in production versions must be used with pagination 
        #which means we shouldnt get all the projects for the user at once 
        #and we camt display them at once in the ui 
        # not efficient for memory and performance 
        # the optimized way is pagination , by displaying a certian number of 
        # projects in a certain number of pages 

        # what we will do in this step is to get the number of projects 
        # for the user by user id ,
        total_projects = await self.collection.count_documents({"owner_id" : owner_id})
        
        # and I will decide page size (did it in the
        # parameter of the function default will be 10 projects per page)

        # and also defined in the parameters the default page that will appear first to the user
        # is page 1 

        #calculate number of pages
        total_pages = total_projects // page_size
        if total_projects % page_size > 0 :     
            total_pages +=1 

        cursor = self.collection.find({"owner_id": owner_id}).sort("_id", -1).skip((page-1)*page_size).limit(page_size)  
        projects = []  
        async for document in cursor:
            projects.append(
                Project(**document)
            )
        return projects , total_pages 
 
