from typing import Dict, Any, Optional, Tuple, Set, Type
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'sqlite:///example.db'  # Replace with your actual database URI
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BaseModel = declarative_base()

def get_db_engine():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class GenerativeRepository:
    def __init__(
        self,
        model: Type[BaseModel],
        db_session: Session = Depends(get_db_engine)
    ):
        self.model = model
        self.db_session = db_session

    def create_record(self, params: Dict[str, Any]) -> int:
        new_record = self.model(**params)
        self.db_session.add(new_record)
        self.db_session.commit()
        self.db_session.refresh(new_record)
        return new_record.id  # Assuming the model has an 'id' field

    def read_record(self, params: Dict[str, Any]):
        return self.db_session.query(self.model).filter_by(**params).first()

    def update_record(self, params: Dict[str, Set[Any]]) -> Optional[Tuple[Any, ...]]:
        record_id = params.pop('id', None)  # Assuming 'id' is used to identify the record
        if record_id is not None:
            record = self.db_session.query(self.model).get(record_id)
            if record:
                for key, value in params.items():
                    setattr(record, key, list(value)[0])
                self.db_session.commit()
                return record
        return None

    def delete_record(self, params: Dict[str, Any]) -> bool:
        record = self.db_session.query(self.model).filter_by(**params).first()
        if record:
            self.db_session.delete(record)
            self.db_session.commit()
            return True
        return False
