from typing import Optional, Dict, Any
from fastapi import Depends
from pydantic import BaseModel

from app.src.common.config.app_settings import get_app_settings, Settings
from app.src.core.schemas.responses.create_lead_response import CreateLeadResponseModel
from app.src.core.schemas.responses.create_lead_type_response import CreateLeadTypeResponseModel
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
