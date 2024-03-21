import json
from pathlib import Path
from typing import Tuple, Any, Dict
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
        self.settings = get_app_settings()
        self.media_repository = MediaRepository()
        self.client = client(service, region_name=self.settings.REGION)
        self.media_bucket = self.settings.MEDIA_BUCKET


class S3Repository(AwsRepository):
    def __init__(self):
        super().__init__('s3')

    def get_media_stream(self, media_code: str) -> Tuple[str, bytes, Any]:
        key = self.media_repository.get_media_name(media_code)
        if not key:
            raise BaseAppException(
                status_code=400,
                description=f"Invalid media code provided {media_code}",
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR,
                data={'media_code': media_code}
            )

        s3_response = self.client.get_object(Bucket=self.media_bucket, Key=key)
        return key, s3_response["Body"].read(), s3_response['ContentType']

    def is_media_uploaded(self, media_name: str) -> bool:
        status = True
        try:
            self.client.head_object(Bucket=self.settings.MEDIA_BUCKET, Key=media_name)
        except Exception as e:
            status = False
        return status

    def download_media(self, bucket_name: str, media_name: str) -> Path:
        file_location = f"./{media_name}"
        self.client.download_file(bucket_name, media_name, file_location)
        return Path(file_location)


class SQSRepository(AwsRepository):
    def __init__(self):
        super().__init__('sqs')

    def send_sqs_message(self, message: Dict[str, Any]) -> None:
        self.client.send_message(
            QueueUrl=self.settings.QUEUE_URL,
            MessageBody=json.dumps(message)
        )
