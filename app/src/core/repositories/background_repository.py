from typing import Dict, Any, List

from sqlalchemy import update, select, text

from app.src.common.config.database import get_mongodb, MongoDB
from app.src.common.enum.background_enums import BackgroundStageEnum
from app.src.core.models.db_models import Media, MediaStatus, User
from app.src.core.repositories.aws_repositories import SQSRepository
from app.src.core.repositories.geniric_repository import GenericDBRepository


class BackgroundRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(None)
        self.mongodb: MongoDB = get_mongodb()
        self.sqs_repository: SQSRepository = SQSRepository()

    def is_media_registered(self, media_code: str) -> bool:
        query = select(Media.media_code).where(Media.media_code == media_code)
        result = self.session.execute(query).fetchone()
        if result:
            return True
        else:
            return False

    def is_media_uploaded(self, media_code: str, bucket: str) -> bool:
        query = select(Media.media_code).filter(Media.media_code == media_code).filter(Media.is_uploaded == True)
        if self.session.execute(query).fetchone():
            return True
        else:
            return False

    def is_transcript_generated(self, media_code: str) -> bool:
        query = (select(MediaStatus.fedbk_status_cd)
                 .join(Media, MediaStatus.media_id == Media.id)
                 .filter(Media.media_code == media_code)
                 .filter(MediaStatus.trans_status_cd == 'S'))
        result = self.session.execute(query).fetchone()
        if result:
            return True
        else:
            return False

    def is_feedback_generated(self, media_code: str) -> bool:
        query = (select(MediaStatus.fedbk_status_cd)
                 .join(Media, MediaStatus.media_id == Media.id)
                 .filter(Media.media_code == media_code)
                 .filter(MediaStatus.fedbk_status_cd == 'S'))
        result = self.session.execute(query).fetchone()
        if result:
            return True
        else:
            return False

    def update_media_attributes(self, attributes: Dict[str, Any]) -> None:
        media_code = attributes.pop('media_code', None)
        query = update(Media).where(Media.media_code == media_code).values(**attributes)
        self.session.execute(query)
        self.session.commit()

    def update_stage(self, media_code: str, stage: BackgroundStageEnum, status_code: str, comments: str,
                     stage_inputs: str = None) -> None:
        media_id = self.get_media_internal_id(media_code)
        status_attrib = {"comments": comments}
        if stage_inputs:
            status_attrib['stage_inputs'] = stage_inputs
        if stage == BackgroundStageEnum.TRANSCRIPTION:
            status_attrib['trans_status_cd'] = status_code
        if stage == BackgroundStageEnum.FEEDBACK:
            status_attrib['fedbk_status_cd'] = status_code

        query = update(MediaStatus).where(MediaStatus.media_id == media_id).values(**status_attrib)
        self.session.execute(query)
        self.session.commit()

    def save_transcription(self, media_code: str, transcription: Dict[str, Any]) -> None:
        self.mongodb.put_transcription({"media_code": media_code, **transcription})

    def get_transcription(self, media_code: str) -> Dict[str, Any]:
        return self.mongodb.get_transcription(media_code)

    def get_systems_messages(self, user_id: str) -> List[Dict[str, Any]]:
        context = [
            "This is a call transcription between a recruiter at Techintelliand a prospect Candidate/JobSeeker.Techintelliis a staffing consultancy that provides recruiting and talent acquisition services to organizations looking to hire for various roles across different Non IT industries.",
            "The recruiter works for Techintelliand has over 5 years of experience in full cycle recruiting. They speak to multiple prospect candidates on a daily basis to understand their needs, and try to close positions given by various clients that the company has.",
            "During calls with prospects, the recruiter explains the Job Description the company is looking for, Responsibilties, Title, Industry,Salary,Location & Willingness to relocate if required, benefits and commercials, and any other as per the requirement. They aim to resolve any questions or concerns Candidates may have about working with designated client for their role fullfillment.",
            "The goal is to close positions by providing an excellent Interview and onboarding experience and demonstrating how Techintellican add value as a strategic talent acquisition partner.",

            "Defined Roles:",

            "Recruiter:  ",
            "Works for  Techintelliwith 5+ years of full life cycle recruiting experience",
            "Has frequent call interactions with candidates to understand their requirements and expereince.",
            "Explains {TECHINTELLI}, client benefits, title, requirements, salary, location and any other details.",
            "Resolves Candidate concerns and questions to secure new client accounts",
            "Aims to close the position.",

            "BDM (Business Development Manager):",
            "Works for Techintelliwith 7+ years of recruitment and BDM experience",
            "Manages and grows relationships with existing candidates",
            "Close final calls with candidates.",
            "Negotiates contracts, makes pricing proposals, and closes deals with new candidates.",
            "Partners with recruiters to ensure successful delivery for client accounts",
            "Seeks to retain and expand key accounts by providing excellent, strategic recruiting services"
        ]

        query = select(User.organization, User.role).where(User.clerk_id == user_id)
        user_details = self.session.execute(query).fetchone()

        messages = [{
            'role': 'system',
            'content': message
        } for message in context]

        return messages

    def get_user_messages(self) -> List[Dict[str, Any]]:
        messages = [
            {
                'type': "overall_feedback",
                'message': {
                    'role': "user",
                    'content': "Generate feedback for the representative"
                }
            },
            {
                'type': "pros",
                'message': {
                    'role': "user",
                    'content': "Generate Procs for representative in 10 points",
                }
            },
            {
                'type': "cons",
                'message': {
                    'role': "user",
                    'content': "Generate Cons for representative in 10 points"
                }
            }
        ]
        return messages

    def get_metric_prompts(self, mcode: str) -> List[Dict[str, Any]]:
        query = text(f"select stage_desc, metric_prompt from metrics_view mv where media_Code='{mcode}' ")

        metrics = []
        for (stage_desc, prompt) in self.session.execute(query).fetchall():
            metrics.append({
                'role': 'user',
                'content': prompt
            })
        return metrics

    def send_feedback_request(self, request: Dict[str, Any]) -> None:
        request['stage'] = BackgroundStageEnum.FEEDBACK.value
        self.sqs_repository.send_sqs_message(request)
