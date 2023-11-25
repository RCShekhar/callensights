import datetime
import json
from typing import Optional, List
from uuid import uuid4
from traceback import format_exc

from fastapi import Depends
import boto3 as aws

from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.core.repositories.media_repository import MediaRepository
from app.src.core.repositories.create_user_repository import UserRepository
from app.src.core.repositories.lead_repository import LeadRepository
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.schemas.responses.upload_response import MediaResponse
from app.src.core.schemas.responses.get_uploads_response import GetUploadsResponseModel


class MediaService:
    def __init__(
            self,
            media_repository: MediaRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ):
        self.media_repository = media_repository
        self.settings = settings
        self.lead_repository = LeadRepository()
        self.user_repository = UserRepository()

    def register_media(self, media_input: UploadMediaInputsModel) -> Optional[List[MediaResponse]]:
        response = []

        request_dump = media_input.model_dump().copy()
        files = request_dump.get('files')
        del request_dump['files']
        for file in files:
            file_response = {}
            media_code = str(uuid4())
            file_type = file.split('.')[-1]
            request_dump['original_name'] = file
            request_dump['file_type'] = file_type
            request_dump['media_code'] = media_code
            request_dump['stored_file'] = media_code + '.' + file_type
            request_dump['bucket'] = self.settings.MEDIA_BUCKET
            request_dump['event_date'] = str(datetime.datetime.now())

            if not self.lead_repository.is_lead_exists(request_dump.get('lead_id')):
                raise BaseAppException(
                    status_code=400,
                    description="Invalid or No such lead exists",
                    custom_error_code=CustomErrorCode.NOT_FOUND_ERROR,
                    data={'lead_id': request_dump.get('lead_id'), 'traceback': format_exc()}
                )

            if not self.user_repository.is_user_exists(request_dump.get('user_id')):
                raise BaseAppException(
                    status_code=401,
                    description="Invlid or No user exists",
                    custom_error_code=CustomErrorCode.NOT_FOUND_ERROR,
                    data={'user_id': request_dump.get('user_id'), 'traceback': format_exc()}
                )

            file_response['file'] = file
            file_response['media_code'] = media_code
            try:
                s3 = aws.client('s3')
                s3_url_response = s3.generate_presigned_post(
                    self.settings.MEDIA_BUCKET,
                    request_dump.get('stored_file'),
                    ExpiresIn=120,
                    Conditions=[
                        [
                            'content-length-range',
                            self.settings.MEDIA_MIN_SIZE,
                            self.settings.MEDIA_MAX_SIZE
                        ]
                    ]
                )
                file_response['presigned_url'] = s3_url_response
                file_response['message'] = "URL Generated"

            except Exception as e:
                file_response['audio_code'] = None
                file_response['presigned_url'] = {}
                file_response['message'] = str(e)

            response.append(MediaResponse.model_validate(file_response))

        return response

    def get_uploads(self, user_id: int) -> List[GetUploadsResponseModel]:

        if not self.user_repository.is_user_exists(user_id):
            raise BaseAppException(
                status_code=401,
                description=f"No user exists with user id {user_id}",
                data={'user_id': user_id, 'traceback': format_exc()}
            )

        records = self.media_repository.get_uploads(user_id)
        response = []
        for record in records:
            data = {
                'media_code': record.media_code,
                'media_type': record.file_type,
                'media_size': record.media_size,
                'media_length': record.media_len,
                'lead_name': record.lead_name,
                'conv_type': record.conv_type
            }

    def _get_new_correlation_id(self) -> str:
        return str(uuid4())
