from fastapi import FastAPI
from  Routers import base  
from  Routers import data   
from pymongo import AsyncMongoClient
from helpers.config import get_settings 

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    """Initialize the MongoDB client on application startup."""
    settings = get_settings()
    app.mongo_connection = AsyncMongoClient(settings.mongo_db_url) 
    app.db_client = app.mongo_connection[settings.mongo_db_name]  # Access the specified database

@app.on_event("shutdown")    
async def shutdown_db_client():
    """Close the MongoDB client on application shutdown."""
    await app.mongo_connection.close()

app.include_router(base.base_router)    
app.include_router(data.data_router)  