from typing import Optional, Any, Dict

from fastapi import Depends
from pydantic import BaseModel

from app.src.core.services.base_service import BaseService
from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.repositories.create_user_repository import UserRepository
from app.src.core.schemas.responses.create_user_response import CreateUserResponse
from app.src.core.schemas.responses.create_user_group_response import CreateUserGroupResponse


class UserService(BaseService):
    def __init__(
            self,
            repository: UserRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ) -> None:
        super().__init__("UserService")
        self.repository = repository
        self.settings = settings

    def create_user(self, model: BaseModel) -> Optional[Dict[str, Any]]:
        user = self.repository.add_user(model)
        return CreateUserResponse.model_validate(
            {
                'user_id': user.id
            }
        ).model_dump()

    def create_user_group(self, model: BaseModel) -> Optional[Dict[str, Any]]:
        user_group = self.repository.add_user_group(model)
        return CreateUserGroupResponse.model_validate(
            {
                'id': user_group.id,
                'group_name': user_group.group_name
            }
        ).model_dump()
