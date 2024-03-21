from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Enum, Date, DateTime

from app.src.core.models.db_models import Base


class Account(Base):
    __tablename__ = 'account'
    account_id = Column(Integer, primary_key=True)
    account_name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255))
    account_status = Column(Enum('Active', 'Inactive'), nullable=False)
    account_owner = Column(String(255), nullable=False)
    account_type = Column(Enum('Client'), default='Client')
    account_website = Column(String(255), nullable=False)
    industry = Column(String(255))
    contract_end_date = Column(Date)
    jobs_submission_workflow = Column(Enum('Vendor', 'Prime Vendor', 'Direct Client'))
    created_by = Column(String(255))
    modified_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.now(UTC))
    modified_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_at = Column(DateTime)
