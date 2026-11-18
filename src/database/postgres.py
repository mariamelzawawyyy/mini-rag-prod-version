from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from ..helpers.config import get_settings
settings = get_settings()

engine = create_async_engine(
    settings.postgres_database_url,
    pool_pre_ping=True,
) 
 
#Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
 
#Database Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 
        

