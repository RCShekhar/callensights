from typing import Optional

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.requests.create_lead_request import CreateLeadRequestModel
from app.src.core.schemas.requests.create_lead_type_request import CreateLeadTypeRequestModel
from app.src.core.models.db_models import LeadTypes
from app.src.core.models.db_models import Lead


class LeadRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(Lead)

    @handle_db_exception
    def add_lead(self, lead_model: CreateLeadRequestModel) -> Optional[Lead]:
        dump = lead_model.model_dump()
        print(dump)
        lead = Lead(**dump)
        self.session.add(lead)
        self.session.commit()
        return lead

    @handle_db_exception
    def add_lead_type(self, type_model: CreateLeadTypeRequestModel) -> Optional[LeadTypes]:
        dump = type_model.model_dump()
        print(dump)
        lead_type = LeadTypes(**dump)
        self.session.add(lead_type)
        self.session.commit()
        return lead_type

    @handle_db_exception
    def is_lead_exists(self, lead_id: int) -> Optional[bool]:
        result = False
        response = self.session.query(self.model).filter_by(id=lead_id).first()

        if response:
            result = True

        return result
