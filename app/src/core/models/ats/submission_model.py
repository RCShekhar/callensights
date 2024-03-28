from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Enum,
    DECIMAL,
    Text,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, relationship

from app.src.core.models.db_models import Base


class Submission(Base):
    __tablename__ = "submissions"
    submission_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = Column(Integer, ForeignKey("job.job_id"), nullable=False)
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    availability: Mapped[Date] = Column(Date, nullable=False)
    engagement_type_id: Mapped[int] = Column(
        Integer, ForeignKey("engagement_types.engagement_type_id"), nullable=False
    )
    pay_type_id: Mapped[int] = Column(
        Integer, ForeignKey("pay_types.pay_type_id"), nullable=False
    )
    bill_rate: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    pay_rate: Mapped[DECIMAL] = Column(DECIMAL(10, 2), nullable=False)
    created_at: Mapped[DateTime] = Column(DateTime, default=datetime.now(UTC))
    modified_at: Mapped[DateTime] = Column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    documents = relationship("SubmissionDocument", back_populates="submission")
    notes = relationship("SubmissionNote", back_populates="submission")
    job = relationship("Job", back_populates="submissions")
    candidate = relationship("Candidate", back_populates="submissions")
    pay_type = relationship("PayType")
    engagement_type = relationship("EngagementType")
    additional_recipients = relationship(
        "SubmissionAdditionalRecipients", back_populates="submission"
    )
    deleted_at: Mapped[DateTime] = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_job_id_candidate_id"),
    )


class SubmissionDocument(Base):
    __tablename__ = "submission_documents"
    document_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = Column(
        Integer, ForeignKey("submissions.submission_id"), nullable=False
    )
    attachment_url: Mapped[str] = Column(String(255), nullable=False)
    submission = relationship("Submission", back_populates="documents")


class SubmissionNote(Base):
    __tablename__ = "submission_notes"
    note_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = Column(
        Integer, ForeignKey("submissions.submission_id"), nullable=False
    )
    note_type: Mapped[str] = Column(
        Enum("Call", "Meeting", "Notes", "Others"), nullable=False
    )
    note: Mapped[Text] = Column(Text, nullable=False)
    file_url: Mapped[str] = Column(String(255))
    submission = relationship("Submission", back_populates="notes")


class SubmissionAdditionalRecipients(Base):
    __tablename__ = "submission_additional_recipients"
    submission_additional_recipients_id: Mapped[int] = Column(
        Integer, primary_key=True, autoincrement=True
    )
    submission_id: Mapped[int] = Column(
        Integer, ForeignKey("submissions.submission_id"), nullable=False
    )
    email: Mapped[str] = Column(String(255), nullable=False)
    submission = relationship("Submission", back_populates="additional_recipients")
