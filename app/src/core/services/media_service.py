from typing import Optional
from uuid import uuid4

from fastapi import Depends
import boto3 as aws

from app.src.core.repositories.upload_media_repository import UploadMediaRepository
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.schemas.responses.upload_response import MediaResponse


class MediaService:
    def __init__(
            self,
            upload_repository: UploadMediaRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ):
        self.repository = upload_repository
        self.settings = settings

    def register_media(self, file: str, media_input: UploadMediaInputsModel) -> Optional[MediaResponse]:
        response = {}

        inputs = media_input.model_dump()
        inputs['file_name'] = file
        file_type = file.split('.')[-1]
        media_code = self._get_new_correlation_id()
        new_media_name = media_code + '.' + file_type
        inputs['media_code'] = media_code
        inputs['new_media_name'] = new_media_name
        del inputs['files']

        self.repository.register_media(inputs)

        try:
            s3 = aws.client('s3')
            s3_url_response = s3.generate_presigned_post(
                self.settings.MEDIA_BUCKET,
                stored_media_file,
                ExpiresIn=120,
                Conditions=[
                    [
                        'content-length-range',
                        self.settings.MEDIA_MIN_SIZE,
                        self.settings.MEDIA_MAX_SIZE
                    ]
                ]
            )
            response['audio_code'] = stored_media_file.split('.')[0]
            response['presigned_url'] = s3_url_response
            response['message'] = "URL Generated"

        except Exception as e:
            response['audio_code'] = None
            response['presigned_url'] = None
            response['message'] = str(e)

        # validate media response
        media_response = MediaResponse.model_validate(**response)

        return media_response

    def _get_new_correlation_id(self) -> str:
        return str(uuid4())
