from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TODO Add settings here
    SECRET: str
    REGION: str
    DEFAULT_SCHEMA: str
    MEDIA_BUCKET: str
    MEDIA_MIN_SIZE: int
    MEDIA_MAX_SIZE: int

    class Config:
        env_file = ".env"


@lru_cache()
def get_app_settings() -> Settings:
    return Settings()
