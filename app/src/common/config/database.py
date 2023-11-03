from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.src.common.config.app_settings import get_app_settings
from app.src.common.config.secret_manager import get_secret


class Database:
    def __init__(self):
        settings = get_app_settings()
        user = get_secret('user')
        password = get_secret('password')
        host = get_secret('host')
        port = get_secret('port')
        schema = settings.DEFAULT_SCHEMA
        self. db_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{schema}"
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(self.engine)


@lru_cache()
def get_db_engine():
    db = Database()
    session = db.Session()
    try:
        yield session
    finally:
        session.close()


