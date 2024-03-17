from pathlib import Path

from app.src.common.config.app_settings import get_app_settings


class AWSService:
    def __init__(self):
        settings = get_app_settings()
        self.sql_db_secret = settings.MYSQLDB_SECRET
        self.mongo_db_secret = settings.MONGODB_SECRET
        self.clerk_secret = settings.CLERK_SECRET
        self.clerk_audience = settings.CLERK_AUDIENCE
        self.region = settings.REGION
        self.media_bucket = settings.MEDIA_BUCKET
        self.download_path = "./"  # settings.STORAGE_MOUNT_PATH

    def download_media(self, bucket_name: str, media_file: str) -> Path:
        pass
