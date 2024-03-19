from sqlalchemy import Column, ForeignKey, Integer, String, Date, Enum, DECIMAL, Boolean, Text, DATETIME, Index

from app.src.core.models.db_models import Base


class Candidate(Base):
    __tablename__ = 'candidate'
    candidate_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    middle_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20))
    mobile = Column(String(20), nullable=False)
    date_of_birth = Column(Date)
    status = Column(Enum('Available', 'Not Available', 'Do Not Call', 'Blacklist', 'Inactive', 'Placed', 'Unsubscribe'))
    OWNER = Column(Integer, ForeignKey('cns_user_def.cu_user_id'))
    job_title = Column(String(255))
    authorization_id = Column(Integer, ForeignKey('work_authorization.authorization_id'), nullable=False)
    source_id = Column(Integer, ForeignKey('source.source_id'))
    years_of_experience = Column(Integer)
    city = Column(String(255))
    country = Column(String(255))
    state = Column(String(255))
    address = Column(Text)
    zip_code = Column(String(10))
    skills = Column(Text)
    soft_skills = Column(Text)
    profile_summary = Column(Text)
    linkedin_url = Column(String(255))
    twitter_url = Column(String(255))
    facebook_url = Column(String(255))
    video_resume = Column(String(255))
    security_clearance = Column(Boolean)
    willing_to_relocate = Column(Boolean)
    employment_type_id = Column(Integer, ForeignKey('employment_type.employment_type_id'), nullable=False)
    account_id = Column(Integer, ForeignKey('account.account_id'))
    contact_name = Column(String(255))
    expected_rate_from = Column(DECIMAL(10, 2))
    expected_rate_to = Column(DECIMAL(10, 2))
    expected_rate_type = Column(Enum('Hourly', 'Daily', 'Weekly', 'Monthly', 'Salary'))
    current_rate_type = Column(Enum('Hourly', 'Daily', 'Weekly', 'Monthly', 'Salary'))
    remote_status = Column(Enum('Remote', 'On Site', 'Hybrid', 'Any'))
    gender = Column(Enum('Male', 'Female', 'Other'))
    current_rate = Column(DECIMAL(10, 2))
    language_id = Column(Integer, ForeignKey('languages_known.language_id'))
    github_url = Column(String(255))
    alternate_email = Column(String(255))
    industry_id = Column(Integer, ForeignKey('industry.industry_id'))
    deleted_at = Column(DATETIME)
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_status', 'status'),
        Index('idx_city', 'city'),
        Index('idx_country', 'country'),
        Index('idx_state', 'state'),
    )


class CandidateResume(Base):
    __tablename__ = 'candidate_resumes'
    resume_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    attachment_url = Column(String(255), nullable=False)
    source_id = Column(Integer, ForeignKey('source.source_id'), nullable=False)
    is_default = Column(Boolean, nullable=False)


class CandidateEducation(Base):
    __tablename__ = 'candidate_education'
    education_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    aggregate = Column(DECIMAL(5, 2))
    category = Column(
        Enum('High School', 'Military Service', 'Vocational School', 'Associate', 'Pre-Bachelors', 'Bachelors',
             'Post-Bachelors', 'Masters', 'Doctorate'), nullable=False)
    attachment_url = Column(String(255))


class CandidateWorkExperience(Base):
    __tablename__ = 'candidate_work_experience'
    experience_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    employer = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    city = Column(String(255))
    country = Column(String(255))
    state = Column(String(255))


class CandidateReference(Base):
    __tablename__ = 'candidate_references'
    reference_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    reference_type = Column(Enum('Other', 'Personal', 'Professional'))
    reference_name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    designation = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    contact_number = Column(String(20))


class Certification(Base):
    __tablename__ = 'certification'
    certification_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    certification_name = Column(String(255), nullable=False)
    completion_date = Column(Date)
    attachment_url = Column(String(255))


class CandidateDocument(Base):
    __tablename__ = 'candidate_documents'
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate.candidate_id'), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(255), nullable=False)
    document_status = Column(Enum('Active', 'Inactive'), nullable=False)
    attachment_url = Column(String(255), nullable=False)
    expiry_date = Column(Date)
