from functools import lru_cache

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from app.src.common.config.app_settings import get_app_settings
from app.src.common.config.secret_manager import get_secret


class Database:
    def __init__(self):
        self. db_url = self.get_db_url()
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(self.engine)

    @classmethod
    def get_db_url(cls):
        settings = get_app_settings()
        url = URL.create(
            "mysql+mysqlconnector",
            username=get_secret('user'),
            password=get_secret('password'),
            host=get_secret('host'),
            database=settings.DEFAULT_SCHEMA
        )
        return url


@lru_cache()
def get_db_engine():
    db = Database()
    session = db.Session()
    return session


