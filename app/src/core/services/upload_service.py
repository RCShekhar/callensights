from typing import Dict, Any, List

from fastapi import Depends, UploadFile
import boto3 as aws

from app.src.core.repositories.upload_repository import UploadMediaRepository
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.common.config.app_settings import get_app_settings, Settings


class UploadMediaService:
    def __init__(
            self,
            upload_repository: UploadMediaRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ):
        self.repository = upload_repository
        self.settings = settings

    def register_media(self, file: UploadFile, input: UploadMediaInputsModel) -> Dict[str, Any]:
        response = {}

        inputs = input.model_dump()
        inputs['file_name'] = file.filename
        validated_inputs = self._validate_inputs(inputs)
        stored_media_file = self.repository.register_media(validated_inputs)

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

        return response


    def _validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return inputs
