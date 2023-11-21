from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.src.common.config.database import get_db_session
from app.src.core.schemas.requests.create_lead_request import CreateLeadRequestModel
from app.src.core.schemas.requests.create_lead_type_request import CreateLeadTypeRequestModel
from app.src.core.models.db_models import LeadTypes
from app.src.core.models.db_models import Lead


class LeadRepository:
    def __init__(
            self,
            db: Session = Depends(get_db_session)
    ) -> None:
        self.db = db

    def add_lead(self, lead_model: CreateLeadRequestModel) -> Optional[Lead]:
        dump = lead_model.model_dump()
        print(dump)
        lead = Lead(**dump)
        self.db.add(lead)
        self.db.commit()
        return lead

    def add_lead_type(self, type_model: CreateLeadTypeRequestModel) -> Optional[LeadTypes]:
        dump = type_model.model_dump()
        print(dump)
        lead_type = LeadTypes(**dump)
        self.db.add(lead_type)
        self.db.commit()
        return lead_type
