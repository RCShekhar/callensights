from typing import Optional, Dict, List, Any

from sqlalchemy import select, update

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.requests.create_lead_request import CreateLeadRequestModel
from app.src.core.schemas.requests.create_lead_type_request import CreateLeadTypeRequestModel
from app.src.core.models.db_models import LeadTypes, Lead, LeadStages, Media, User


class LeadRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(Lead)

    @handle_db_exception
    def add_lead(self, lead_model: CreateLeadRequestModel) -> Optional[Lead]:
        dump = lead_model.model_dump()
        row = self.session.execute(
            select(LeadStages.id.label("stage_id")).where(LeadStages.code == dump['stage_code'])
        ).fetchone()
        dump.update(row._asdict())

        row = self.session.execute(
            select(User.id.label("assigned_to")).where(User.clerk_id == dump.get("user_id"))
        ).fetchone()
        dump.update(row._asdict())
        del dump['user_id']
        del dump['stage_code']
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

    @handle_db_exception
    def get_stages(self) -> List[Dict[str, Any]]:
        stmt = select(
            LeadStages.id.label("stage_id"),
            LeadStages.code.label("stage_name")
        ).where(LeadStages.is_active == True)

        cursor = self.session.execute(stmt)
        stages = []
        for rec in cursor.fetchall():
            stages.append(rec._asdict())

        return stages

    @handle_db_exception
    def get_assigned_leads(self, user_id: str) -> List[Dict[str, Any]]:
        stmt = (select(
            Lead.id.label("lead_id"),
            Lead.name.label("lead_name"),
            Lead.stage_id.label("stage_id")
        ).join(
            User,
            User.id == Lead.assigned_to
        ).where(User.clerk_id == user_id))

        leads_cursor = self.session.execute(stmt)
        leads = [lead._asdict() for lead in leads_cursor.fetchall()]
        return leads

    @handle_db_exception
    def is_assigned_to(self, lead_id: int, user_id: int) -> bool:
        stmt = select(Lead.id).where(Lead.assigned_to == user_id)
        cursor = self.session.execute(stmt)
        if cursor.first() is None:
            return False
        return True

    @handle_db_exception
    def get_lead_info(self, lead_id: int) -> Dict[str, Any]:
        stmt = select(
            Lead.id.label("lead_id"),
            Lead.name.label("lead_name"),
            Lead.email.label("email"),
            Lead.phone.label("phone"),
            Lead.lead_desc.label("description")
        ).where(Lead.id == lead_id)

        row = self.session.execute(stmt).first()
        return dict(row)

    @handle_db_exception
    def get_lead_conversations(self, lead_id: int, user_id: str) -> List[Dict[str, Any]]:
        stmt = select(
            Media.media_code("media_code"),
            Media.event_date("event_date")
        ).join(
            User,
            User.id == Media.user_id
        ).where(
            User.clerk_id == user_id and Media.lead_id == lead_id
        ).order_by(Media.event_date.desc())

        result = self.session.execute(stmt).fetchall()
        rows = [dict(row) for row in result]
        return rows

    @handle_db_exception
    def update_stage(self, lead_id: int, stage_id: int) -> bool:
        stmt = update(Lead).where(Lead.id == lead_id).values({'stage_id': stage_id})
        self.session.execute(stmt)
        self.session.commit()
        return True
