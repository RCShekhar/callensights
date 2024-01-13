import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # AWS Config
    MONGODB_SECRET: str = os.environ['MONGODB_SECRET']
    MYSQLDB_SECRET: str = os.environ['MYSQLDB_SECRET']
    CLERK_SECRET: str = os.environ['CLERK_SECRET']
    CLERK_AUDIENCE: str = os.environ['CLERK_AUDIENCE']
    REGION: str = os.environ['REGION']

    # Database Configuration
    DEFAULT_SCHEMA: str = os.environ['DEFAULT_SCHEMA']

    # AWS Buckets
    MEDIA_BUCKET: str = os.environ['MEDIA_BUCKET']
    TRANSCRIPT_BUCKET: str = os.environ['TRANSCRIPT_BUCKET']
    ANALYSIS_BUCKET: str = os.environ['ANALYSIS_BUCKET']

    # Application configuration
    MEDIA_MIN_SIZE: int = os.environ['MEDIA_MIN_SIZE']
    MEDIA_MAX_SIZE: int = os.environ['MEDIA_MAX_SIZE']
    IS_LOCAL: Optional[bool] = os.environ.get('IS_LOCAL', False)

    # class Config:
    #     env_file = ".env"


@lru_cache()
def get_app_settings() -> Settings:
    return Settings()
