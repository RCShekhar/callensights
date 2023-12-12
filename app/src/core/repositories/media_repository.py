from typing import Dict, Any, List, Optional

from sqlalchemy import Row, select
from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.models.db_models import Media, Lead, User
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.common.config.database import get_mongodb


class MediaRepository(GenericDBRepository):
    def __init__(
            self
    ):
        super().__init__(Media)
        self.mongo_db = get_mongodb()

    @handle_db_exception
    def register_media(self, media_model: Dict[str, Any]) -> bool:
        response = False
        clerk_id = media_model.get('user_id')
        # media_model['clerk_id'] = clerk_id
        media_model['user_id'] = self.get_id_for_clerk(clerk_id)
        model = self.model(**media_model)
        self.session.add(model)
        self.session.commit()
        response = True

        return response

    @handle_db_exception
    def get_id_for_clerk(self, clerk_id: str) -> int:
        stmt = select(User.id.label("user_id")).where(User.clerk_id == clerk_id)
        row = self.session.execute(stmt).fetchone()
        user_id = row._asdict().get("user_id")
        return user_id

    @handle_db_exception
    def get_uploads(self, user_id: int) -> List[Row]:
        records = (self.session.query(
            Media.media_code.label("media_code"),
            Media.file_type.label("media_type"),
            Media.media_size.label("media_size"),
            Media.media_len.label("media_length"),
            Lead.name.label("lead_name"),
            Media.conv_type.label("conv_type")
        ).join(
            Lead,
            Lead.id == Media.lead_id
        ).filter(Media.user_id == user_id).all())

        return records

    @handle_db_exception
    def get_media_name(self, media_code) -> Optional[str]:
        rows = (self.session.query(
            Media.stored_file
        ).filter(Media.media_code == media_code).all())

        if not rows:
            return None

        return rows[0][0]

    def get_feedback(self, media_code: str) -> Any:
        if self.has_uploaded(media_code):
            return self.mongo_db.get_feedback(media_code)

    def get_transcription(self, media_code: str) -> Any:
        if self.has_uploaded(media_code):
            return self.mongo_db.get_transcription(media_code)
