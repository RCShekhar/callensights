from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.common.config.database import get_db_session
from app.src.core.models.db_models import User, UserGroup
from app.src.core.schemas.requests.create_user_request import CreateUserRequest
from app.src.core.schemas.requests.create_user_group_request import CreateUserGroupRequest


class UserRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(User)

    # @handle_db_exception
    def add_user(self, user_model: CreateUserRequest) -> User:
        dump = user_model.model_dump()
        user = User(**dump)
        self.session.add(user)
        self.session.commit()
        return user

    # @handle_db_exception
    def add_user_group(self, user_group_model: CreateUserGroupRequest) -> UserGroup:
        user_group = UserGroup(**user_group_model.model_dump())
        self.session.add(user_group)
        self.session.commit()
        return user_group

    def is_user_exists(self, user_id: int) -> bool:
        result: bool = False
        response = self.session.query(User).filter_by(id=user_id)
        if response:
            result = True
        return result


