from datetime import datetime, UTC

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Enum, DECIMAL, Text, DateTime

from app.src.core.models.db_models import Base


class Submission(Base):
    __tablename__ = 'submissions'
    submission_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('job.job_id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    availability = Column(Date, nullable=False)
    engagement_type_id = Column(Integer, ForeignKey('engagement_types.engagement_type_id'), nullable=False)
    pay_type_id = Column(Integer, ForeignKey('pay_types.pay_type_id'), nullable=False)
    bill_rate = Column(DECIMAL(10, 2))
    pay_rate = Column(DECIMAL(10, 2), nullable=False)
    additional_recipients = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now(UTC))
    modified_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_at = Column(DateTime)


class SubmissionDocument(Base):
    __tablename__ = 'submission_documents'
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.submission_id'), nullable=False)
    attachment_url = Column(String(255), nullable=False)


class SubmissionNote(Base):
    __tablename__ = 'submission_notes'
    note_id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.submission_id'), nullable=False)
    note_type = Column(Enum('Call', 'Meeting', 'Notes', 'Others'), nullable=False)
    note = Column(Text, nullable=False)
    file_url = Column(String(255))
