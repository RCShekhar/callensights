from sqlalchemy import Column, ForeignKey, Integer, String, Date, Enum, DECIMAL, Boolean, Text, DATETIME, Index
from sqlalchemy.orm import Mapped

from app.src.core.models.db_models import Base


class Candidate(Base):
    __tablename__ = 'candidate'
    candidate_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = Column(String(255), nullable=False)
    middle_name: Mapped[str] = Column(String(255))
    last_name: Mapped[str] = Column(String(255))
    email: Mapped[str] = Column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = Column(String(20))
    mobile: Mapped[str] = Column(String(20), nullable=False)
    date_of_birth: Mapped[Date] = Column(Date)
    status: Mapped[str] = Column(
        Enum('Available', 'Not Available', 'Do Not Call', 'Blacklist', 'Inactive', 'Placed', 'Unsubscribe'))
    OWNER: Mapped[int] = Column(Integer, ForeignKey('cns_user_def.cu_user_id'))
    job_title: Mapped[str] = Column(String(255))
    authorization_id: Mapped[int] = Column(Integer, ForeignKey('work_authorization.authorization_id'), nullable=False)
    source_id: Mapped[int] = Column(Integer, ForeignKey('source.source_id'))
    years_of_experience: Mapped[int] = Column(Integer)
    city: Mapped[str] = Column(String(255))
    country: Mapped[str] = Column(String(255))
    state: Mapped[str] = Column(String(255))
    address: Mapped[Text] = Column(Text)
    zip_code: Mapped[str] = Column(String(10))
    skills: Mapped[Text] = Column(Text)
    soft_skills: Mapped[Text] = Column(Text)
    profile_summary: Mapped[Text] = Column(Text)
    linkedin_url: Mapped[str] = Column(String(255))
    twitter_url: Mapped[str] = Column(String(255))
    facebook_url: Mapped[str] = Column(String(255))
    video_resume: Mapped[str] = Column(String(255))
    security_clearance: Mapped[Boolean] = Column(Boolean)
    willing_to_relocate: Mapped[Boolean] = Column(Boolean)
    employment_type_id: Mapped[int] = Column(Integer, ForeignKey('employment_type.employment_type_id'), nullable=False)
    account_id: Mapped[int] = Column(Integer, ForeignKey('account.account_id'))
    contact_name: Mapped[str] = Column(String(255))
    expected_rate_from: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    expected_rate_to: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    expected_rate_type: Mapped[str] = Column(Enum('Hourly', 'Daily', 'Weekly', 'Monthly', 'Salary'))
    current_rate_type: Mapped[str] = Column(Enum('Hourly', 'Daily', 'Weekly', 'Monthly', 'Salary'))
    remote_status: Mapped[str] = Column(Enum('Remote', 'On Site', 'Hybrid', 'Any'))
    gender: Mapped[str] = Column(Enum('Male', 'Female', 'Other'))
    current_rate: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    language_id: Mapped[int] = Column(Integer, ForeignKey('languages_known.language_id'))
    github_url: Mapped[str] = Column(String(255))
    alternate_email: Mapped[str] = Column(String(255))
    industry_id: Mapped[int] = Column(Integer, ForeignKey('industry.industry_id'))
    deleted_at: Mapped[DATETIME] = Column(DATETIME)
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_status', 'status'),
        Index('idx_city', 'city'),
        Index('idx_country', 'country'),
        Index('idx_state', 'state'),
    )


class CandidateResume(Base):
    __tablename__ = 'candidate_resumes'
    resume_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    attachment_url: Mapped[str] = Column(String(255), nullable=False)
    source_id: Mapped[int] = Column(Integer, ForeignKey('source.source_id'), nullable=False)
    is_default: Mapped[Boolean] = Column(Boolean, nullable=False)


class CandidateEducation(Base):
    __tablename__ = 'candidate_education'
    education_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    institution: Mapped[str] = Column(String(255), nullable=False)
    degree: Mapped[str] = Column(String(255), nullable=False)
    start_date: Mapped[Date] = Column(Date)
    end_date: Mapped[Date] = Column(Date)
    aggregate: Mapped[DECIMAL] = Column(DECIMAL(5, 2))
    category: Mapped[str] = Column(
        Enum('High School', 'Military Service', 'Vocational School', 'Associate', 'Pre-Bachelors', 'Bachelors',
             'Post-Bachelors', 'Masters', 'Doctorate'), nullable=False)
    attachment_url: Mapped[str] = Column(String(255))


class CandidateWorkExperience(Base):
    __tablename__ = 'candidate_work_experience'
    experience_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    employer: Mapped[str] = Column(String(255), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    start_date: Mapped[Date] = Column(Date)
    end_date: Mapped[Date] = Column(Date)
    city: Mapped[str] = Column(String(255))
    country: Mapped[str] = Column(String(255))
    state: Mapped[str] = Column(String(255))


class CandidateReference(Base):
    __tablename__ = 'candidate_references'
    reference_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    reference_type: Mapped[str] = Column(Enum('Other', 'Personal', 'Professional'))
    reference_name: Mapped[str] = Column(String(255), nullable=False)
    company_name: Mapped[str] = Column(String(255))
    designation: Mapped[str] = Column(String(255), nullable=False)
    email: Mapped[str] = Column(String(255), nullable=False)
    contact_number: Mapped[str] = Column(String(20))


class Certification(Base):
    __tablename__ = 'certification'
    certification_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    certification_name: Mapped[str] = Column(String(255), nullable=False)
    completion_date: Mapped[Date] = Column(Date)
    attachment_url: Mapped[str] = Column(String(255))


class CandidateDocument(Base):
    __tablename__ = 'candidate_documents'
    document_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    document_name: Mapped[str] = Column(String(255), nullable=False)
    document_type: Mapped[str] = Column(String(255), nullable=False)
    document_status: Mapped[str] = Column(Enum('Active', 'Inactive'), nullable=False)
    attachment_url: Mapped[str] = Column(String(255), nullable=False)
    expiry_date: Mapped[Date] = Column(Date)
