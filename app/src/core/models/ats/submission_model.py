from datetime import datetime, UTC

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Enum, DECIMAL, Text, DateTime
from sqlalchemy.orm import Mapped

from app.src.core.models.db_models import Base


class Submission(Base):
    __tablename__ = 'submissions'
    submission_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = Column(Integer, ForeignKey('job.job_id'), nullable=False)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    availability: Mapped[Date] = Column(Date, nullable=False)
    engagement_type_id: Mapped[int] = Column(Integer, ForeignKey('engagement_types.engagement_type_id'), nullable=False)
    pay_type_id: Mapped[int] = Column(Integer, ForeignKey('pay_types.pay_type_id'), nullable=False)
    bill_rate: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    pay_rate: Mapped[DECIMAL] = Column(DECIMAL(10, 2), nullable=False)
    additional_recipients: Mapped[Text] = Column(Text)
    notes: Mapped[Text] = Column(Text)
    created_at: Mapped[DateTime] = Column(DateTime, default=datetime.now(UTC))
    modified_at: Mapped[DateTime] = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_at: Mapped[DateTime] = Column(DateTime)


class SubmissionDocument(Base):
    __tablename__ = 'submission_documents'
    document_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = Column(Integer, ForeignKey('submissions.submission_id'), nullable=False)
    attachment_url: Mapped[str] = Column(String(255), nullable=False)


class SubmissionNote(Base):
    __tablename__ = 'submission_notes'
    note_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = Column(Integer, ForeignKey('submissions.submission_id'), nullable=False)
    note_type: Mapped[str] = Column(Enum('Call', 'Meeting', 'Notes', 'Others'), nullable=False)
    note: Mapped[Text] = Column(Text, nullable=False)
    file_url: Mapped[str] = Column(String(255))
