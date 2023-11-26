from typing import Tuple
from boto3 import client
from fastapi import Depends

from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.repositories.media_repository import MediaRepository

class AwsRepository:
    def __init__(self,
                 service
                 ) -> None:
        settings = get_app_settings()
        self.media_repository = MediaRepository()
        self.client = client(service, region_name=settings.REGION)
        self.media_bucket = settings.MEDIA_BUCKET


class S3Repository(AwsRepository):
    def __init__(self):
        super().__init__('s3')

    def get_media_stream(self, media_code: str) -> Tuple[str, bytes]:
        key = self.media_repository.get_media_name(media_code)
        if not key:
            raise BaseAppException(
                status_code=400,
                description=f"Invalid media code provided {media_code}",
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR,
                data={'media_code': media_code}
            )

        s3_response = self.client.get_object(Bucket=self.media_bucket, Key=key)
        return key, s3_response["Body"].read()

