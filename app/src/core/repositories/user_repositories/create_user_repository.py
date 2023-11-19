from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.common.config.database import get_db_session
from app.src.core.models.db_models import User, UserGroup
from app.src.core.schemas.requests.create_user_request import CreateUserRequest
from app.src.core.schemas.requests.create_user_group_request import CreateUserGroupRequest


class UserRepository:
    def __init__(
            self,
            db: Session = Depends(get_db_session)
    ) -> None:
        self.db = db

    # @handle_db_exception
    def add_user(self, user_model: CreateUserRequest) -> User:
        dump = user_model.model_dump()
        print(dump)
        user = User(**dump)
        self.db.add(user)
        self.db.commit()
        return user

    # @handle_db_exception
    def add_user_group(self, user_group_model: CreateUserGroupRequest) -> UserGroup:
        user_group = UserGroup(**user_group_model.model_dump())
        self.db.add(user_group)
        self.db.commit()
        return user_group


