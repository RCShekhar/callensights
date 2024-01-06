from typing import Dict, Any, Type

from app.src.common.config.database import Database
from app.src.core.models.db_models import Base, Activity
from app.src.common.decorators.db_exception_handlers import handle_db_exception


class GenericDBRepository:
    def __init__(
            self,
            model: Type[Base]
    ):
        self.db: Database = Database()
        self.session = self.db.Session()
        self.model: Base = model

    @handle_db_exception
    def insert(self, record: Dict[str, Any]) -> Base:
        model_record = self.model(**record)
        self.session.add(model_record)
        self.session.commit()
        return model_record

    @handle_db_exception
    def record_activity(self, params: Dict[str, Any]) -> None:
        activity = Activity(**params)
        self.session.add(activity)
        self.session.commit()


