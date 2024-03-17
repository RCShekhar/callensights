from typing import Dict, Any

from sqlalchemy import update, select

from app.src.common.config.database import get_mongodb, MongoDB
from app.src.common.enum.background_enums import BackgroundStageEnum
from app.src.core.models.db_models import Media, MediaStatus
from app.src.core.repositories.geniric_repository import GenericDBRepository


class BackgroundRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(None)
        self.mongodb: MongoDB = get_mongodb()

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

    def update_stage(self, media_code: str, stage: BackgroundStageEnum, status_code: str, comments: str) -> None:
        media_id = self.get_media_internal_id(media_code)
        status_attrib = {"comments": comments}
        if stage == BackgroundStageEnum.TRANSCRIPTION:
            status_attrib['trans_status_cd'] = status_code
        if stage == BackgroundStageEnum.FEEDBACK:
            status_attrib['fedbk_status_cd'] = status_code

        query = update(MediaStatus).where(MediaStatus.media_id == media_id).values(**status_attrib)
        self.session.execute(query)
        self.session.commit()

    def save_transcription(self, media_code: str, transcription: Dict[str, Any]) -> None:
        self.mongodb.put_transcription({"media_code": media_code, **transcription})
