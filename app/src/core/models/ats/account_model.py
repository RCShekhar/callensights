from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Enum, Date, DateTime
from sqlalchemy.orm import Mapped, relationship

from app.src.core.models.db_models import Base


class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[int] = Column("account_id", Integer, primary_key=True)
    account_name: Mapped[str] = Column(
        "account_name", String(255), nullable=False, unique=True
    )
    display_name: Mapped[str] = Column("display_name", String(255))
    account_status: Mapped[str] = Column(
        "account_status", Enum("Active", "Inactive"), nullable=False
    )
    account_owner: Mapped[str] = Column("account_owner", String(255), nullable=False)
    account_type: Mapped[str] = Column("account_type", Enum("Client"), default="Client")
    account_website: Mapped[str] = Column(
        "account_website", String(255), nullable=False
    )
    industry: Mapped[str] = Column("industry", String(255))
    contract_end_date: Mapped[datetime] = Column("contract_end_date", Date)
    candidates = relationship("Candidate", back_populates="account")
    jobs_submission_workflow: Mapped[str] = Column(
        "jobs_submission_workflow", Enum("Vendor", "Prime Vendor", "Direct Client")
    )
    created_by: Mapped[str] = Column("created_by", String(255))
    modified_by: Mapped[str] = Column("modified_by", String(255))
    created_at: Mapped[datetime] = Column(
        "created_at", DateTime, default=datetime.now(UTC)
    )
    modified_at: Mapped[datetime] = Column(
        "modified_at", DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    deleted_at: Mapped[datetime] = Column("deleted_at", DateTime)
