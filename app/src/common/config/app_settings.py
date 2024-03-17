from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TODO Add settings here

    # AWS Config
    MONGODB_SECRET: str
    MYSQLDB_SECRET: str
    CLERK_SECRET: str
    CLERK_AUDIENCE: str
    REGION: str
    QUEUE_URL: str

    # Database Configuration
    DEFAULT_SCHEMA: str

    # AWS Buckets
    MEDIA_BUCKET: str

    # Application configuration
    MEDIA_MIN_SIZE: int
    MEDIA_MAX_SIZE: int
    IS_LOCAL: bool

    class Config:
        env_file = ".env"


@lru_cache()
def get_app_settings() -> Settings:
    return Settings()
