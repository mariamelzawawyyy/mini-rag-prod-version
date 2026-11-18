from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env")

    app_name: str
    model_api_key: SecretStr 
    file_allowed_types: list[str]
    file_max_size: int
    file_default_chunk_size: int
    mongo_db_url: str
    mongo_db_name: str
    postgres_username: str
    postgres_password: SecretStr
    postgres_host: str
    postgres_port: int
    postgres_main_db: str
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int

    @property
    #@property is a built in python decorator that turns a class method into a
    # variable we can actually use , the postgres url is computed from 
    # the pre existing enviroment variables above  
    def postgres_database_url(self) -> str:
        username = quote_plus(self.postgres_username)
        password = quote_plus(self.postgres_password.get_secret_value())
        return (
            f"postgresql+asyncpg://{username}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_main_db}"
        )


@lru_cache
# the object is made only once from th settings class and everytime we 
# call an instance of it it returns the object made

# without it everytime we want to call an instance fromm get_settings
# it will make another object and read the whole .env again
def get_settings() -> Settings:
    """Get application settings (created once, then reused)"""
    return Settings()          
         
