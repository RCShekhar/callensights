import datetime
import io
from typing import Optional, List, Dict, Any
from uuid import uuid4

import boto3 as aws
from fastapi import Depends
from fastapi.responses import StreamingResponse

from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.repositories.aws_repositories import S3Repository
from app.src.core.repositories.media_repository import MediaRepository
from app.src.core.schemas.responses.get_uploads_response import GetUploadsResponseModel
from app.src.core.schemas.responses.upload_response import MediaResponse


class MediaService:
    def __init__(
            self,
            media_repository: MediaRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ):
        self.media_repository = media_repository
        self.settings = settings
        self.s3_repository = S3Repository()

    def register_media(self, media_input: Dict[str, Any]) -> Optional[List[MediaResponse]]:
        response = []

        request_dump = media_input
        files = request_dump.get('files')
        del request_dump['files']

        self.media_repository.assume_lead_exists(request_dump.get('lead_id'))
        self.media_repository.assume_user_exists(request_dump.get('user_id'))

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

            activity = self.media_repository.register_media(request_dump)

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
            self.media_repository.record_activity(activity)

        return response

    def get_uploads(self, user_id: str) -> List[GetUploadsResponseModel]:
        self.media_repository.assume_user_exists(user_id)

        records = self.media_repository.get_uploads(user_id)
        response = [GetUploadsResponseModel.model_validate(record._asdict()) for record in records]
        return response

    def get_media_stream(self, media_code: str, user_id: str) -> StreamingResponse:
        self.media_repository.assume_media_assigned_to(media_code, user_id)

        key, media_content, content_type = self.s3_repository.get_media_stream(media_code)
        if media_content is not None:
            return StreamingResponse(
                io.BytesIO(media_content),
                media_type=content_type
            )

    def get_feedback(self, media_code: str, user_id: str) -> Any:
        self.media_repository.assume_media_assigned_to(media_code, user_id)

        if self.media_repository.is_feedback_generated(media_code):
            return self.media_repository.get_feedback(media_code)
        else:
            return {
                'media_code': media_code,
                'status': 'Feedback generation is still under progress'
            }

    def get_transcription(self, media_code: str, user_id: str):
        self.media_repository.assume_media_assigned_to(media_code, user_id)
        if self.media_repository.is_transcript_generated(media_code):
            return self.media_repository.get_transcription(media_code)
        else:
            return {
                'media_code': media_code,
                'status': 'Transcription generation is still under process'
            }
