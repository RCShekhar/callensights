from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import Row, select, update
from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.common.exceptions.exceptions import NotAssignedToUserException
from app.src.core.models.db_models import Media, Lead, User, MediaStatus
from app.src.core.repositories.user_repository import UserRepository
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.common.config.database import get_mongodb


class MediaRepository(GenericDBRepository):
    def __init__(self):
        super().__init__(Media)
        self.mongo_db = get_mongodb()
        self.user_repository = UserRepository()

    @handle_db_exception
    def register_media(self, media_model: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        clerk_id = media_model.get("user_id")
        # media_model['clerk_id'] = clerk_id
        media_model["user_id"] = self.user_repository.get_internal_user_id(clerk_id)
        model = self.model(**media_model)
        self.session.add(model)
        self.session.commit()
        activity = {
            "done_by": self.user_repository.get_internal_user_id(clerk_id),
            "lead_id": media_model.get("lead_id"),
            "activity_code": "UPLOAD",
            "activity_desc": "Media uploaded",
            "event_date": datetime.now(),
            "stage_id": media_model.get("stage_id"),
            "media_code": media_model.get("media_code"),
        }

        return activity

    @handle_db_exception
    def get_id_for_clerk(self, clerk_id: str) -> int:
        stmt = select(User.id.label("user_id")).where(User.clerk_id == clerk_id)
        row = self.session.execute(stmt).fetchone()
        user_id = row._asdict().get("user_id")
        return user_id

    @handle_db_exception
    def get_uploads(self, user_id: str) -> List[Row]:
        user_cur = self.session.execute(select(User.role).where(User.clerk_id == user_id))
        user_role, = user_cur.fetchone()

        query = (
            select(
                Media.media_code.label("media_code"),
                Media.file_type.label("media_type"),
                Media.media_size.label("media_size"),
                Media.media_len.label("media_length"),
                Media.event_date.label("created_date"),
                User.clerk_id.label("user_id"),
                User.user_name.label("user_name"),
                Lead.id.label("lead_id"),
                Lead.name.label("lead_name"),
                Media.conv_type.label("conv_type")
            ).join(
                Lead,
                Lead.id == Media.lead_id,
                isouter=True
            ).join(
                User,
                User.id == Media.user_id
            )
        )
        if user_role.upper() != 'ADMIN':
            query = query.filter(
                User.clerk_id == user_id
            )

        print("Get Uploads query:", query)
        print("user_id", user_id)

        records = self.session.execute(query).all()

        return records

    @handle_db_exception
    def get_media_name(self, media_code) -> Optional[str]:
        rows = (
            self.session.query(Media.stored_file)
            .filter(Media.media_code == media_code)
            .all()
        )

        if not rows:
            return None

        return rows[0][0]

    def get_feedback(self, media_code: str) -> Dict[str, Any]:
        if self.is_uploaded(media_code):
            return self.mongo_db.get_feedback(media_code)

    def get_transcription(self, media_code: str) -> Any:
        if self.is_uploaded(media_code):
            return self.mongo_db.get_transcription(media_code)

    def is_assigned_to(self, media_code: str, user_id: str) -> bool:
        result: bool = False

        query = (
            select(Media.media_code)
            .join(User, User.id == Media.user_id)
            .filter(User.clerk_id == user_id)
            .filter(Media.media_code == media_code)
        )

        rec = self.session.execute(query).fetchone()
        if rec:
            result = True

        return result

    def assume_media_assigned_to(self, media_code: str, user_id: str) -> None:
        if self.user_repository.is_admin(user_id):
            return

        if not self.is_assigned_to(media_code, user_id):
            raise NotAssignedToUserException(
                data={"media_code": media_code, "user_id": user_id}
            )

    @handle_db_exception
    def is_uploaded(self, media_code: str) -> bool:
        query = select(Media.is_uploaded).where(Media.media_code == media_code)
        (status,) = self.session.execute(query).fetchone()

        return status

    @handle_db_exception
    def is_feedback_generated(self, media_code) -> bool:
        return_value = False

        query = (
            select(MediaStatus.fedbk_status_cd)
            .join(Media, Media.id == MediaStatus.media_id)
            .filter(Media.media_code == media_code)
        )

        row = self.session.execute(query).fetchone()
        (status,) = row
        if status in ["S", "C"]:
            return_value = True

        return return_value

    @handle_db_exception
    def is_transcript_generated(self, media_code) -> bool:
        return_value = False

        query = (
            select(MediaStatus.trans_status_cd)
            .join(Media, Media.id == MediaStatus.media_id)
            .filter(Media.media_code == media_code)
        )

        row = self.session.execute(query).fetchone()
        (status,) = row
        if status in ["S", "C"]:
            return_value = True

        return return_value

    @handle_db_exception
    def update_media_attributes(self, media_code: str,  **kwargs) -> None:
        stmt = update(Media).where(Media.media_code == media_code).values(kwargs)
        self.session.execute(stmt)
        self.session.commit()
