from typing import Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends

from app.src.common.config.database import get_db_session
from app.src.common.constants.global_constants import PROC_PARAMS
from app.src.core.models.db_models import Media


class UploadMediaRepository:
    def __init__(
            self,
            db_session: Session = Depends(get_db_session)
    ):
        self.db_session = db_session

    # TODO add db exception handler decorator
    def register_media(self, params: Dict[str, Any]) -> str:
        proc_params = ', '.join([':' + param for param in PROC_PARAMS])
        proc_inputs = {param: params.get(param) for param in PROC_PARAMS}

        media = Media()

        self.db_session.execute(
            text(f"CALL proc_insert_upload({proc_params}, @new_file)"),
            proc_inputs
        )
        new_file = self.db_session.execute(text("SELECT @new_file")).fetchone()[0]

        return new_file
