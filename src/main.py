from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from .database.postgres import engine
from .database.mongo import mongo_client
from .database.mongo import mongo_client, mongo_db

from .routers import auth_router, base_router, data_router, project_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        # Startup: Check PostgreSQL connection
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        # Startup: Check MongoDB connection
        await mongo_client.admin.command("ping")

        app.db_client = mongo_db

        yield

    finally:
        # Shutdown: Close database connections
        await engine.dispose()
        await mongo_client.close()


app = FastAPI(
    title="Mini RAG API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router)  
app.include_router(base_router)  
app.include_router(project_router)  
app.include_router(data_router)   
  
  