from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    ENVIRONMENT: str = "local" # local | dev | staging | production
    PROJECT_NAME: str = "Blog Content Automation"
    cors_origins_raw: str = "*"
    base_dir: str = str(Path(__file__).resolve().parent.parent)

    STABILITY_API_KEY: str #성능 이슈로 사용x
    OPENAI_API_KEY: str
    
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin]


@lru_cache()
def get_settings():
    return Settings()
