from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Module identity
    module_name: str = "App"
    module_version: str = "1.0.0"

    # Database
    database_url: str = "postgresql+asyncpg://cicor:cicor@localhost:5432/cicor"

    # CORS
    cors_origins: list[str] = ["http://localhost:4321", "http://localhost:3000"]

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
