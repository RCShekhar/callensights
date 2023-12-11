import select
from typing import List, Any, Dict

from sqlalchemy import select, update, delete

from app.src.core.repositories.geniric_repository import GenericDBRepository
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
        manager_id = None
        if user_model.manager_id is not None and user_model.manager_id != "":
            manager_id, = self.session.execute(select(User.id).where(User.clerk_id == user_model.manager_id)).fetchone()
        user_dump = user_model.model_dump()
        user_dump['clerk_id'] = user_dump['user_name']
        user_dump['manager_id'] = manager_id

        user = User(**user_dump)
        self.session.add(user)
        self.session.commit()
        return user

    # @handle_db_exception
    def add_user_group(self, user_group_model: CreateUserGroupRequest) -> UserGroup:
        user_group = UserGroup(**user_group_model.model_dump())
        self.session.add(user_group)
        self.session.commit()
        return user_group

    def is_user_exists(self, user_id: str) -> bool:
        result: bool = False
        response = self.session.query(User).filter_by(clerk_id=user_id)
        if response:
            result = True
        return result

    def get_team(self, user_id: str) -> List[Any]:
        cte = select(User.id, User.clerk_id).where(User.clerk_id == user_id).cte(recursive=True)
        cte = cte.union_all(
            select(User.id, User.clerk_id).where(User.manager_id == cte.c.id)
        )
        result = self.session.execute(select([cte]))
        return [usr_id for usr_id, in result.all()]

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        cte = update(User).where(User.clerk_id == user_id).values(user_data)
        self.session.execute(cte)
        self.session.commit()

    def delete_user(self, user_id: str) -> None:
        cte = delete(User).where(User.clerk_id == user_id)
        self.session.execute(cte)
        self.session.commit()
