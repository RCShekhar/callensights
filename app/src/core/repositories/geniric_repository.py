from typing import Generic, Dict, Any, Optional, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import insert

from app.src.common.config.database import Database, get_db_session
from app.src.core.models.db_models import Base

GenericModel = TypeVar("GenericModel")


class GenericDBRepository(Generic[GenericModel]):
    def __init__(
            self,
            model: Generic[Base],
            session: Session = Depends(get_db_session)
    ):
        self.session: Session = session
        self.model: Base = model

    def insert(self, record: Dict[str, Any]) -> GenericModel:
        model_record = self.model(**record)
        self.session.add(model_record)
        self.session.commit()
        return model_record


