from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import insert

from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.exceptions.exceptions import NoUserFoundException, NotAssignedToUserException, NoLeadFoundException
from app.src.core.repositories.user_repository import UserRepository
from app.src.core.repositories.lead_repository import LeadRepository
from app.src.core.schemas.responses.create_lead_response import CreateLeadResponseModel
from app.src.core.schemas.responses.create_lead_type_response import CreateLeadTypeResponseModel
from app.src.core.schemas.responses.lead_info_response import LeadInfoResponse
from app.src.core.services.base_service import BaseService


class LeadService(BaseService):
    def __init__(
            self,
            repository: LeadRepository = Depends(),
            settings: Settings = Depends(get_app_settings)
    ):
        super().__init__("LeadService")
        self.user_repository = UserRepository()
        self.repository = repository
        self.settings = settings

    def create_lead(self, model: BaseModel, user_id: str) -> Optional[Dict[str, Any]]:
        self._assume_user_exists(user_id)

        dump = model.model_dump()
        dump['user_id'] = user_id
        lead = self.repository.add_lead(dump)
        return CreateLeadResponseModel.model_validate(
            {
                'lead_id': lead.id
            }
        ).model_dump()

    def create_lead_type(self, model: BaseModel, user_id: str) -> Optional[Dict[str, Any]]:
        dump = model.model_dump()
        dump['user_id'] = user_id
        lead_type = self.repository.add_lead_type(dump)
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

    def update_stage(self, lead_id: int, user_id: str, stage_id: int) -> Optional[str]:
        self._assume_lead_exists(lead_id)
        self._assume_user_exists(user_id)
        self._assume_lead_assigned_to(lead_id, user_id)

        activity = self.repository.update_stage(lead_id, stage_id, user_id)
        self.repository.record_activity(activity)
        return "SUCCESS"

    def assign_to(self, lead_ids: List[int], user_id: str, target_user: str) -> List[Dict[str, Any]]:
        response = []
        has_target_user: bool = False
        self._assume_user_exists(user_id)
        is_admin = self.repository.is_admin_user(user_id)

        if target_user is not None or target_user != '':
            has_target_user = not has_target_user
            self._assume_user_exists(target_user)

        for lead_id in lead_ids:
            status = 'SUCCESS'
            self._assume_lead_exists(lead_id)

            to_user = user_id
            if is_admin and has_target_user:
                activity = self.repository.assign_lead(lead_id, target_user)
                to_user = target_user
                self.repository.record_activity(activity)
            elif not is_admin:
                activity = self.repository.assign_lead(lead_id, user_id)
                self.repository.record_activity(activity)
            else:
                to_user = None
                status = 'FAILED'

            response.append(
                {
                    'lead_id': lead_id,
                    'assign_to': to_user,
                    'status': status
                }
            )

        return response

    def _assume_lead_exists(self, lead_id: int) -> None:
        if not self.repository.is_lead_exists(lead_id):
            raise NoLeadFoundException(
                data={"lead_id": lead_id}
            )

    def _assume_lead_assigned_to(self, lead_id: int, user_id: str) -> None:
        if self.user_repository.is_admin(user_id):
            return

        if not self.repository.is_assigned_to(lead_id, user_id):
            raise NotAssignedToUserException(
                data={"lead_id": lead_id, "user_id": user_id}
            )

    def _assume_user_exists(self, user_id: str) -> None:
        user_repository = UserRepository()
        if not user_repository.is_user_exists(user_id):
            raise NoUserFoundException(
                data={"user_id": user_id}
            )

    def add_comment(self, lead_id: int, user_id: str, user_comment: str) -> str:
        self._assume_lead_exists(lead_id)
        self._assume_user_exists(user_id)
        self._assume_lead_assigned_to(lead_id, user_id)

        activity = {
            'done_by': self.user_repository.get_user_id(user_id),
            'lead_id': lead_id,
            'activity_code': 'COMMENT',
            'activity_desc': user_comment,
            'event_date': datetime.now()
        }

        self.repository.record_activity(activity)
        return 'SUCCESS'