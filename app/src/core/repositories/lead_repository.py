from typing import Optional, Dict, List, Any

from sqlalchemy import select, update

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.models.db_models import LeadTypes, Lead, LeadStages, Media, User
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.requests.create_lead_type_request import CreateLeadTypeRequestModel


class LeadRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(Lead)

    @handle_db_exception
    def add_lead(self, lead_model: Dict[str, Any]) -> Optional[Lead]:
        dump = lead_model
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
    def add_lead_type(self, type_model: Dict[str, Any]) -> Optional[LeadTypes]:
        lead_type = LeadTypes(**type_model)
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
        ).where(LeadStages.is_active is True)

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
    def is_assigned_to(self, lead_id: int, user_id: str) -> bool:
        stmt = select(
            Lead.id
        ).join(
            User, User.id == Lead.assigned_to
        ).where(User.clerk_id == user_id and Lead.id == lead_id)

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
        return row._asdict()

    @handle_db_exception
    def get_lead_conversations(self, lead_id: int, user_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(
                Media.media_code.label("media_code"),
                Media.event_date.label("event_date"),
                Media.conv_type.label("call_type"),
                Lead.name.label("lead_name"),
                Lead.country.label("country"),
                Lead.st_province.label("state")
            ).join(
                User,
                User.id == Media.user_id
            ).join(
                Lead,
                Lead.id == Media.lead_id
            ).filter(
                User.clerk_id == user_id
            ).filter(
                Media.lead_id == lead_id
            ).order_by(Media.event_date.desc())
        )
        print(stmt)

        result = self.session.execute(stmt).fetchall()
        rows = [row._asdict() for row in result]
        return rows

    @handle_db_exception
    def update_stage(self, lead_id: int, stage_id: int) -> bool:
        stmt = update(Lead).where(Lead.id == lead_id).values({'stage_id': stage_id})
        self.session.execute(stmt)
        self.session.commit()
        return True

    @handle_db_exception
    def is_admin_user(self, user_id: str) -> bool:
        query = select(User.id).filter(User.clerk_id == user_id).filter(User.role == 'ADMIN')
        row = self.session.execute(query).fetchone()
        status = True if row else False
        return status

    @handle_db_exception
    def assign_lead(self, lead_id: int, user_id: str) -> None:
        user_query = select(User.id.label('user_id')).where(User.clerk_id == user_id)
        uid, = self.session.execute(user_query).fetchone()
        query = update(Lead).where(Lead.id == lead_id).values(
            {
                'assigned_to': uid
            }
        )
        self.session.execute(query)
        self.session.commit()
