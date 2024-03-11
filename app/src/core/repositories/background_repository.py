from typing import Dict, Any

from app.src.common.config.database import get_mongodb, MongoDB
from app.src.common.enum.background_enums import BackgroundStageEnum
from app.src.core.models.db_models import Media
from app.src.core.repositories.geniric_repository import GenericDBRepository


class BackgroundRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(None)
        self.mongodb: MongoDB = get_mongodb()

    def is_media_registered(self, media_code: str) -> bool:
        return True

    def is_media_uploaded(self, media_file: str, bucket: str) -> bool:
        return True

    def is_transcript_generated(self, media_coe: str) -> bool:
        return True

    def is_feedback_generated(self, media_code: str) -> bool:
        return True

    def update_media_attributes(self, attributes: Dict[str, Any]) -> None:
        pass

    def update_stage(self, stage: BackgroundStageEnum, status_code: str, comments: str) -> None:
        pass

    def save_transcription(self, media_code: str, transcription: str) -> None:
        pass
