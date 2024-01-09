from functools import lru_cache
from typing import Optional, Dict, Any

from pymongo.results import InsertOneResult
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

from app.src.common.config.secret_manager import SecretManager
from app.src.common.config.app_settings import get_app_settings


class Database:
    def __init__(self):
        self.secret_mgr = SecretManager()
        self.db_url = self.get_db_url()
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(self.engine)

    def get_db_url(self) -> URL:
        settings = get_app_settings()
        url = URL.create(
            "mysql+mysqlconnector",
            username=self.secret_mgr.mysql_db_secret('username'),
            password=self.secret_mgr.mysql_db_secret('password'),
            host=self.secret_mgr.mysql_db_secret('host'),
            database=settings.DEFAULT_SCHEMA
        )
        return url


class MongoDB:
    """
    MongoDB Connector class for inserting transcriptions.
    """

    def __init__(self, database="callensights"):
        self.database = database
        self.settings = get_app_settings()
        self.secret_mgr = SecretManager()
        self.client: Optional[MongoClient] = None

    def get_connection(self):
        """
        Get MongoDB connection using the provided credentials.
        """

        user_name = self.secret_mgr.mongo_db_secret('username')
        password = self.secret_mgr.mongo_db_secret('password')
        host = self.secret_mgr.mongo_db_secret("host")
        mongo_url = f"mongodb+srv://{user_name}:{password}@{host}/?retryWrites=true&w=majority"
        self.client = MongoClient(mongo_url)
        return self.client

    def put_feedback(self, feedback, collection_name="feedbacks") -> InsertOneResult:
        """
        Insert feedback data into MongoDB.
        """
        with self.get_connection() as client:
            db = client[self.database]
            collection = db[collection_name]
            return collection.insert_one(feedback)

    def get_transcription(self, media_code: str, collection_name:str="transcriptions") -> Dict[str, Any]:
        """
        Get transcription data from the MongoDB.
        """
        with self.get_connection() as client:
            db = client[self.database]
            collection = db[collection_name]
            response = collection.find_one({"media_code": media_code})
            response = dict(response).copy()
            del response['_id']
            return response

    def put_transcription(self, transcription, collection_name="transcriptions") -> InsertOneResult:
        """
        Insert transcription data into MongoDB.
        """
        with self.get_connection() as client:
            db = client[self.database]
            collection = db[collection_name]
            return collection.insert_one(transcription)

    def get_feedback(self, media_code: str, collection_name="feedbacks") -> str:
        """
        Get Feedback data from the MongoDB.
        """
        with self.get_connection() as client:
            db = client[self.database]
            collection = db[collection_name]
            response = collection.find_one({"media_code": media_code})
            response = dict(response).copy()
            del response['_id']
            return response


def get_db_session():
    db = Database()
    session = db.Session()

    try:
        return session
    finally:
        session.close()


@lru_cache
def get_mongodb():
    db = MongoDB()
    return db
