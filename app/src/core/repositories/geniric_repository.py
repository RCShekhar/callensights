from typing import Dict, Any, Type

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.common.config.database import get_db_session
from app.src.core.models.db_models import Base
from app.src.common.decorators.db_exception_handlers import handle_db_exception


class GenericDBRepository:
    def __init__(
            self,
            model: Type[Base],
            # session: Session = Depends(get_db_session)
    ):
        self.session: Session = get_db_session()
        self.model: Base = model

    @handle_db_exception
    def insert(self, record: Dict[str, Any]) -> Base:
        model_record = self.model(**record)
        self.session.add(model_record)
        self.session.commit()
        return model_record


