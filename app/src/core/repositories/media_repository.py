from typing import Dict, Any, List, Optional

from sqlalchemy import Row
from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.models.db_models import Media, Lead
from app.src.core.repositories.geniric_repository import GenericDBRepository


class MediaRepository(GenericDBRepository):
    def __init__(
            self
    ):
        super().__init__(Media)

    @handle_db_exception
    def register_media(self, media_model: Dict[str, Any]) -> bool:
        response = False
        model = self.model(**media_model)
        self.session.add(model)
        self.session.commit()
        response = True

        return response

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
