from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
   app_name: str  
   model_api_key: str  
   file_allowed_types: list  
   file_max_size: int   
   file_default_chunk_size: int    

   class Config:
        env_file = ".env"

def get_settings():
    """Get application settings."""
    return Settings()          
         
