from typing import Dict, Any

from sqlalchemy import Row, select
from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.common.config.database import get_mongodb
from app.src.core.models.db_models import Media


class AnalyticsRepository(GenericDBRepository):
    def __init__(self):
        super().__init__(Media)
        self.mongo_db = get_mongodb()

    @handle_db_exception
    def get_all_feedbacks(self) -> Dict[str, Any]:
        return self.mongo_db.get_feedbacks()
