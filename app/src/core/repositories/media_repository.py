from typing import Dict, Any, List, Type

from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends

from app.src.common.config.database import get_db_session
from app.src.common.constants.global_constants import PROC_PARAMS
from app.src.core.models.db_models import Media, Lead
from app.src.core.repositories.geniric_repository import GenericDBRepository


class MediaRepository(GenericDBRepository):
    def __init__(
            self
    ):
        super().__init__(Media)

    # TODO add db exception handler decorator
    def register_media(self, params: Dict[str, Any]) -> str:
        proc_params = ', '.join([':' + param for param in PROC_PARAMS])
        proc_inputs = {param: params.get(param) for param in PROC_PARAMS}

        media = Media()

        self.session.execute(
            text(f"CALL proc_insert_upload({proc_params}, @new_file)"),
            proc_inputs
        )
        new_file = self.session.execute(text("SELECT @new_file")).fetchone()[0]

        return new_file

    def get_uploads(self, user_id: int) -> List[Type[Media]]:
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
        ).filter_by(user_id=user_id).all())

        return records
