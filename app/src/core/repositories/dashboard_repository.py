import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta

from typing import Any, Dict, List, Optional

from sqlalchemy import select, func

from app.src.common.config.database import MongoDB, get_mongodb
from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.models.db_models import User, Media, Lead
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.repositories.media_repository import MediaRepository


class DashboardRepository(GenericDBRepository):
    def __init__(
            self
    ) -> None:
        super().__init__(User)
        self.media_repository = MediaRepository()
        self.mongodb: MongoDB = get_mongodb()

    @handle_db_exception
    def get_uploads(self, user_id: str) -> List[str]:
        query = select(
            Media.media_code.label("media_code"),
            Media.media_len.label("media_length"),
            Media.media_size.label("media_size")
        ).join(
            User,
            User.clerk_id == Media.user_id
        )
        if not self.is_admin(user_id):
            query = query.filter(User.clerk_id == user_id)

        media_codes = [r._asdict() for r in self.session.execute(query).fetchall()]
        return media_codes

    @handle_db_exception
    def get_media_metrics(self, media_code: str) -> Optional[Dict[str, Any]]:
        response = {'media_code': media_code}
        if not self.media_repository.is_feedback_generated(media_code):
            return response

        feedback = self.mongodb.get_feedback(media_code)
        if not feedback:
            return response

        metrics = feedback.get('metrics')
        return metrics


    @handle_db_exception
    def get_monthly_uploads(self, user_id) -> List[Dict[str, int]]:
        query = self.session.query(
            func.extract('month', Media.event_date).label('month'),
            func.count(Media.id).label('calls_uploaded')
        )

        if not self.is_admin(user_id):
            query = query.filter(Media.user_id == self.get_internal_user_id(user_id))

        # Filter by event_date (last 12 months)
        one_year_ago = datetime.now() - relativedelta(years=1)
        query = query.filter(Media.event_date >= one_year_ago)

        # Group by month
        query = query.group_by('month')

        rs = query.all()

        results = {calendar.month_name[r.month]: r.calls_uploaded for r in rs}

        # Ensure all months are present in the result
        for i in range(1, 13):
            month = calendar.month_name[i]
            if month not in results:
                results[month] = 0

        return results

    def get_recent_calls(self, user_id) -> List[Dict[str, Any]]:
        query = select(
            Media.media_code.label('media_code'),
            Lead.name.label("lead_name"),
            User.clerk_id.label("user_id"),
            User.user_name.label("user_name"),
            Lead.stage_id.label("stage_id"),
            Media.event_date.label("created_dt")
        ).join(
            Lead,
            Lead.id == Media.lead_id
        ).join(
            User,
            User.id == Media.user_id
        )

        if not self.is_admin(user_id):
            query = query.filter(User.clerk_id == user_id)

        result = self.session.execute(query).fetchmany(5)
        return [row._asdict() for row in result]

