from typing import Optional, Any, Dict

from fastapi import Depends
from pydantic import BaseModel

from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException
from app.src.core.schemas.responses.user_workspace_response import UserWorkspaceResponse, StageInfo, LeadPosition
from app.src.core.services.base_service import BaseService
from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.repositories.create_user_repository import UserRepository
from app.src.core.schemas.responses.create_user_response import CreateUserResponse
from app.src.core.schemas.responses.create_user_group_response import CreateUserGroupResponse
from app.src.core.schemas.requests.update_user_request import UpdateUserRequest
from app.src.core.repositories.lead_repository import LeadRepository


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

    def update_user(self, user_id: str, user_details: UpdateUserRequest) -> str:
        status = "FAILED"
        if not self.repository.is_user_exists(user_id):
            raise BaseAppException(
                status_code=404,
                description="No Such User found",
                data={"user_id": user_id},
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR
            )

        self.repository.update_user(user_id, user_details.model_dump())
        status = "SUCCESS"

        return status

    def delete_user(self, user_id: str) -> str:
        status = "FAILED"
        if not self.repository.is_user_exists(user_id):
            raise BaseAppException(
                status_code=404,
                description="No Such User found",
                data={"user_id": user_id},
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR
            )

        self.repository.delete_user(user_id)
        satus = "SUCCESS"
        return status

    def get_user_workspace(
            self,
            user_id: str,
    ) -> UserWorkspaceResponse:
        lead_repo: LeadRepository = LeadRepository()
        if not self.repository.is_user_exists(user_id):
            raise BaseAppException(
                status_code=404,
                description="No Such User found",
                data={"user_id": user_id},
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR
            )

        stages = lead_repo.get_stages()
        leads = lead_repo.get_assigned_leads(user_id)

        workspace_response = UserWorkspaceResponse(stages=stages, leads=leads)
        return workspace_response
