from typing import Dict, Any, Type

from sqlalchemy import select

from app.src.common.config.database import Database
from app.src.common.exceptions.exceptions import NoUserFoundException, NoLeadFoundException, NotAssignedToUserException
from app.src.core.models.db_models import Base, Activity, Lead, User
from app.src.common.decorators.db_exception_handlers import handle_db_exception


class GenericDBRepository:
    def __init__(
            self,
            model: Type[Base]
    ):
        self.db: Database = Database()
        self.session = self.db.Session()
        self.model: Base = model

    @handle_db_exception
    def insert(self, record: Dict[str, Any]) -> Base:
        model_record = self.model(**record)
        self.session.add(model_record)
        self.session.commit()
        return model_record

    @handle_db_exception
    def record_activity(self, params: Dict[str, Any]) -> None:
        activity = Activity(**params)
        self.session.add(activity)
        self.session.commit()

    @handle_db_exception
    def is_user_exists(self, user_id: str) -> bool:
        result: bool = False
        # query = select(User).where(User.clerk_id==user_id)
        response = self.session.query(User).filter_by(clerk_id=user_id)
        if response:
            result = True
        return result

    def assume_user_exists(self, user_id: str) -> None:
        if not self.is_user_exists(user_id):
            raise NoUserFoundException(
                data={'user_id': user_id}
            )

    def assume_lead_exists(self, lead_id: int) -> None:
        if not self.is_lead_exists(lead_id):
            raise NoLeadFoundException(
                data={"lead_id": lead_id}
            )

    @handle_db_exception
    def is_lead_exists(self, lead_id: int) -> bool:
        result = False
        query = select(Lead.id).where(Lead.id == lead_id)
        response, = self.session.execute(query).fetchone()
        if response:
            result = True
        return result

    @handle_db_exception
    def is_admin(self, user_id: str) -> bool:
        query = select(User.role).where(User.clerk_id == user_id)
        role, = self.session.execute(query).fetchone()
        return role == 'ADMIN'

    @handle_db_exception
    def get_user_id(self, clerk_id: str) -> int:
        query = select(User.id).where(User.clerk_id == clerk_id)
        uid, = self.session.execute(query).fetchone()
        return uid

    def assume_lead_assigned_to(self, lead_id: int, user_id: str) -> None:
        if self.is_admin(user_id):
            return
        if not self.is_assigned_to(lead_id, user_id):
            raise NotAssignedToUserException(
                data={"lead_id": lead_id, "user_id": user_id}
            )

    @handle_db_exception
    def is_assigned_to(self, lead_id: int, user_id: str) -> bool:
        stmt = select(
            Lead.id
        ).join(
            User, User.id == Lead.assigned_to
        ).where(User.clerk_id == user_id and Lead.id == lead_id)
        cursor = self.session.execute(stmt)
        if cursor.first() is None:
            return False
        return True
