import os
import traceback
from pathlib import Path
from typing import Dict, Any

import openai
from fastapi import Depends, BackgroundTasks
from openai import OpenAI
from sqlalchemy.exc import SQLAlchemyError

from app.src.common.app_logging.logging import logger
from app.src.common.config.secret_manager import SecretManager
from app.src.common.enum.background_enums import BackgroundStageEnum, BackgroundTaskStatusEnum
from app.src.core.repositories.aws_repositories import S3Repository
from app.src.core.repositories.background_repository import BackgroundRepository
from app.src.core.schemas.requests.background_requests import BackgroundTaskRequestModel
from app.src.core.schemas.responses.background_response import BackgroundTaskResponseModel
from app.src.core.services.base_service import BaseService
from app.src.core.services.feedback_service import FeedbackService
from app.src.core.services.transcription_service import TranscriptionService


class BackgroundService(BaseService):
    def __init__(
            self,
            repository: BackgroundRepository = Depends(),
            feedback_service: FeedbackService = Depends(),
            transcription_service: TranscriptionService = Depends()
    ) -> None:
        super().__init__("BackgroundTasks")
        self.transcription_service = transcription_service
        self.feedback_service = feedback_service
        self.repository = repository
        self.s3_repository = S3Repository()
        self.GPT_MODEL = 'gpt-4'
        self.MAX_MESSAGES = 10

    async def generate_transcription(
            self,
            request: Dict[str, Any]
    ):
        media_code = request.get('media_code')
        media_file = request.get('media_file')
        bucket = request.get('media_bucket')

        self.repository.update_media_attributes(
            {
                "media_code": media_code,
                "media_size": request.get('media_size'),
                "media_len": request.get("media_length")
            })

        logger.debug("Transcription process started")
        self.repository.update_stage(
            media_code,
            BackgroundStageEnum.TRANSCRIPTION,
            'R',
            'Transcription Started',
            str(request)
        )

        local_media: Path = Path()
        try:
            logger.debug(f"downloading media file {media_file}")
            local_media: Path = self.s3_repository.download_media(bucket, media_file)
            logger.debug("Generating transcription")
            transcription = self.transcription_service.generate_transcription(local_media)
            self.repository.save_transcription(media_code, transcription)
            self.repository.send_feedback_request(request)
            self.repository.update_stage(
                media_code,
                BackgroundStageEnum.TRANSCRIPTION,
                'S',
                "Transcription Generated Successfully.."
            )
        except SQLAlchemyError as e:
            logger.error(f"TRANSCRIPTION_ERROR: {e}")
            logger.error(traceback.format_exc())
            self.repository.update_stage(
                media_code,
                BackgroundStageEnum.TRANSCRIPTION,
                'F',
                f'ERROR: {e}'
            )
            return
        except Exception as e:
            logger.error(f"TRANSCRIPTION_ERROR: {e}")
            logger.error(traceback.format_exc())
            self.repository.update_stage(
                media_code,
                BackgroundStageEnum.TRANSCRIPTION,
                'F',
                f'ERROR: {e}'
            )
            return
        finally:
            if local_media.is_file():
                local_media.unlink()

    def run_background_task(
            self,
            user_id: str,
            inputs: BackgroundTaskRequestModel,
            bg_tasks: BackgroundTasks
    ) -> BackgroundTaskResponseModel:
        return_value = BackgroundTaskResponseModel(
            status=BackgroundTaskStatusEnum.FAILED.value,
            comment=f'{inputs.stage.value}Task Registered Successfully..'
        )
        media_code = inputs.media_code
        media_file = inputs.media_file

        if not self.repository.is_media_registered(media_code):
            return_value.comment = f"No such media registered {media_code}"
            logger.warning(return_value.comment)
        elif not self.s3_repository.is_media_uploaded(media_file):
            return_value.comment = f"No media uploaded for media code {media_code}"
            logger.warning(return_value.comment)
        else:
            return_value.status = BackgroundTaskStatusEnum.SUCCESS.value

        if return_value.status == BackgroundTaskStatusEnum.FAILED.value:
            return return_value

        if inputs.stage == BackgroundStageEnum.TRANSCRIPTION:
            if self.repository.is_transcript_generated(media_code):
                return_value.comment = f"Transcription already generated for {media_code}"
                return return_value

            params = inputs.model_dump()
            params['stage'] = params['stage'].value if params['stage'] else None
            params['user_id'] = user_id
            bg_tasks.add_task(
                self.generate_transcription, params
            )
        elif inputs.stage == BackgroundStageEnum.FEEDBACK:
            if not self.repository.is_transcript_generated(media_code):
                return_value.status = BackgroundTaskStatusEnum.FAILED
                return_value.comment = f"No Transcription generated for the media {media_code}"
                return return_value
            elif self.repository.is_feedback_generated(media_code):
                return_value.comment = f"Feedback already generated for media {media_code}"
                return return_value

            input_dict = inputs.model_dump()
            bg_tasks.add_task(
                self.generate_feedback,
                input_dict
            )
        else:
            return BackgroundTaskResponseModel(
                status=BackgroundTaskStatusEnum.FAILED,
                comments=f"Invalid stage  {inputs.stage}"
            )
        return return_value

    async def generate_feedback(
            self,
            request: Dict[str, Any]
    ):
        client = OpenAI(api_key=SecretManager().get_openai_secret())
        media_code = request.get('media_code')
        user_id = request.get('user_id')

        logger.info("Feedback Generation started")

        self.repository.update_stage(
            media_code,
            BackgroundStageEnum.FEEDBACK,
            'R',
            "Feedback Generation Started..",
            stage_inputs=str(request)
        )

        try:
            transcription = self.repository.get_transcription(media_code)
            logger.info(f"API_KEY: *******{openai.api_key[-3:]}")

            feedback = {}
            record = {'media_code': media_code, 'feedback': feedback}
            messages = []
            messages += self.repository.get_systems_messages(user_id)
            messages.append({
                'role': 'user',
                'content': transcription['text']
            })
            client.chat.completions.create(
                model=self.GPT_MODEL,
                messages=messages[-self.MAX_MESSAGES:]
            )

            for question in self.repository.get_user_messages():
                question_type = question.get('type')
                messages.append(question.get('message'))
                completion = client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=messages[-self.MAX_MESSAGES:]
                )
                m = completion.choices[0].message
                messages.append(m)
                feedback[question_type] = m.content.split('\n')
            else:
                messages.append({
                    'role': 'user',
                    'content': 'Provide rating for following metrics based out of 10 and give only number'
                })
                completion = client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=messages[-self.MAX_MESSAGES:]
                )
                messages.append(completion.choices[0].message)

            metrics = []
            feedback['metrics'] = metrics
            for question in self.repository.get_metric_prompts(media_code):
                messages.append(question)
                completion = client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=messages[-self.MAX_MESSAGES:]
                )
                msg = completion.choices[0].message
                messages.append(msg)
                metrics.append({
                    'metric_name': question.get('content'),
                    'rating': msg.content,
                    'absolute_rating': msg.content + "/10"
                })
            logger.info("Feedback generated..")
            self.repository.mongodb.put_feedback(record)
            logger.info("Feedback stored successfully")

            self.repository.update_stage(
                media_code,
                BackgroundStageEnum.FEEDBACK,
                'S',
                "Feedback generation completed Successfully.."
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            self.repository.update_stage(
                media_code,
                BackgroundStageEnum.FEEDBACK,
                'F',
                f"ERROR: {e}"
            )
