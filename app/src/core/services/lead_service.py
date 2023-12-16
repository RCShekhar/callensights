from typing import Optional, Dict, Any
from fastapi import Depends
from pydantic import BaseModel

from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException
from app.src.core.repositories.create_user_repository import UserRepository
from app.src.core.schemas.responses.create_lead_response import CreateLeadResponseModel
from app.src.core.schemas.responses.create_lead_type_response import CreateLeadTypeResponseModel
from app.src.core.schemas.responses.lead_info_response import LeadInfoResponse, LeadConversation
from app.src.core.services.base_service import BaseService
from app.src.core.repositories.lead_repository import LeadRepository


class LeadService(BaseService):
    def __init__(
            self,
            repository: LeadRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ):
        super().__init__("LeadService")
        self.repository = repository
        self.settings = settings

    def create_lead(self, model: BaseModel) -> Optional[Dict[str, Any]]:
        lead = self.repository.add_lead(model)
        return CreateLeadResponseModel.model_validate(
            {
                'lead_id': lead.id
            }
        ).model_dump()

    def create_lead_type(self, model: BaseModel) -> Optional[Dict[str, Any]]:
        lead_type = self.repository.add_lead_type(model)
        return CreateLeadTypeResponseModel.model_validate(
            {
                'id': lead_type.id
            }
        ).model_dump()

    def get_lead_info(self, lead_id: int, user_id: str) -> LeadInfoResponse:
        self._assume_lead_exists(lead_id)
        self._assume_user_exists(user_id)
        self._assume_lead_assigned_to(lead_id, user_id)

        data = self.repository.get_lead_info(lead_id)
        data['conversations'] = self.repository.get_lead_conversations(lead_id, user_id)

        # data['conversations'] = [LeadConversation(**conversation) for conversation in data['conversations']]
        response = LeadInfoResponse(**data)
        return response

    def update_stage(self, lead_id: int, user_id: str) -> Optional[str]:
        self._assume_lead_exists(lead_id)
        self._assume_user_exists(user_id)
        self._assume_lead_assigned_to(lead_id, user_id)

        self.repository.update_stage(lead_id)
        return "SUCCESS"

    def _assume_lead_exists(self, lead_id: int) -> None:
        if not self.repository.is_lead_exists(lead_id):
            raise BaseAppException(
                status_code=405,
                description="Invalid lead id or no lead exists",
                data={"lead_id": lead_id},
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR
            )

    def _assume_lead_assigned_to(self, lead_id: int, user_id: str) -> None:
        if not self.repository.is_assigned_to(lead_id, user_id):
            raise BaseAppException(
                status_code=404,
                description="The given lead not assigned to user",
                data={"lead_id": lead_id, "user_id": user_id},
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR
            )

    def _assume_user_exists(self, user_id: str) -> None:
        user_repository = UserRepository()
        if not user_repository.is_user_exists(user_id):
            raise BaseAppException(
                status_code=405,
                description="No such user exists",
                data={"user_id": user_id},
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR
            )
