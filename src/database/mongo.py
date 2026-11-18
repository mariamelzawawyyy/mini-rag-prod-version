from pymongo import AsyncMongoClient
from ..helpers.config import get_settings 

settings = get_settings()

mongo_client = AsyncMongoClient(settings.mongo_db_url)

mongo_db = mongo_client[settings.mongo_db_name]
 
async def get_mongo_db():
    return mongo_db

async def close_mongo_connection():
    await mongo_client.close()    