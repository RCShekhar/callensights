from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Enum,
    DECIMAL,
    Boolean,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, relationship

from app.src.core.models.db_models import Base


from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Enum,
    Text,
    Boolean,
    DECIMAL,
    ForeignKey,
    DateTime,
    Index,
    SmallInteger,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func


class Candidate(Base):
    __tablename__ = "candidate"
    candidate_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = Column(String(255), nullable=False)
    middle_name: Mapped[str] = Column(String(255))
    last_name: Mapped[str] = Column(String(255))
    email: Mapped[str] = Column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = Column(String(20))
    mobile: Mapped[str] = Column(String(20), nullable=False)
    date_of_birth: Mapped[Date] = Column(Date)
    candidate_status: Mapped[str] = Column(
        Enum(
            "Available",
            "Not Available",
            "Do Not Call",
            "Blacklist",
            "Inactive",
            "Placed",
            "Unsubscribe",
        )
    )
    owner_id: Mapped[int] = Column(Integer, ForeignKey("cns_user_def.cu_user_id"))
    job_title: Mapped[str] = Column(String(255))
    authorization_id: Mapped[int] = Column(
        SmallInteger, ForeignKey("work_authorization.authorization_id"), nullable=False
    )
    source_id: Mapped[int] = Column(SmallInteger, ForeignKey("source.source_id"))
    years_of_experience: Mapped[int] = Column(Integer)
    city: Mapped[str] = Column(String(255))
    country: Mapped[str] = Column(String(255))
    state: Mapped[str] = Column(String(255))
    address: Mapped[Text] = Column(Text)
    zip_code: Mapped[str] = Column(String(10))
    profile_summary: Mapped[Text] = Column(Text)
    linkedin_url: Mapped[str] = Column(String(255))
    twitter_url: Mapped[str] = Column(String(255))
    facebook_url: Mapped[str] = Column(String(255))
    video_resume: Mapped[str] = Column(String(255))
    security_clearance: Mapped[Boolean] = Column(Boolean)
    willing_to_relocate: Mapped[Boolean] = Column(Boolean)
    employment_type_id: Mapped[int] = Column(
        SmallInteger, ForeignKey("employment_type.employment_type_id"), nullable=False
    )
    account_id: Mapped[int] = Column(Integer, ForeignKey("account.account_id"))
    contact_name: Mapped[str] = Column(String(255))
    expected_rate_from: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    expected_rate_to: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    expected_rate_type: Mapped[str] = Column(
        Enum("Hourly", "Daily", "Weekly", "Monthly", "Salary")
    )
    current_rate_type: Mapped[str] = Column(
        Enum("Hourly", "Daily", "Weekly", "Monthly", "Salary")
    )
    remote_status: Mapped[str] = Column(Enum("Remote", "On Site", "Hybrid", "Any"))
    gender: Mapped[str] = Column(Enum("Male", "Female", "Other"))
    current_rate: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    language_id: Mapped[int] = Column(
        SmallInteger, ForeignKey("languages_known.language_id")
    )
    github_url: Mapped[str] = Column(String(255))
    alternate_email: Mapped[str] = Column(String(255))
    industry_id: Mapped[int] = Column(SmallInteger, ForeignKey("industry.industry_id"))
    created_at: Mapped[DateTime] = Column(DateTime, default=func.now())
    owner = relationship("User", back_populates="candidates")
    work_authorization = relationship("WorkAuthorization", back_populates="candidates")
    source = relationship("Source", back_populates="candidates")
    employment_type = relationship("EmploymentType", back_populates="candidates")
    account = relationship("Account", back_populates="candidates")
    languages_known = relationship("LanguagesKnown", back_populates="candidates")
    industry = relationship("Industry", back_populates="candidates")
    documents = relationship("CandidateDocument", back_populates="candidates")
    education = relationship("CandidateEducation", back_populates="candidates")
    references = relationship("CandidateReference", back_populates="candidates")
    resumes = relationship("CandidateResume", back_populates="candidates")
    work_experiences = relationship(
        "CandidateWorkExperience", back_populates="candidates"
    )
    certifications = relationship("Certification", back_populates="candidates")
    skills = relationship("CandidateSkill", back_populates="candidate")
    soft_skills = relationship("CandidateSoftSkill", back_populates="candidate")
    submissions = relationship("Submission", back_populates="candidate")
    modified_at: Mapped[DateTime] = Column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[DateTime] = Column(DateTime)
    __table_args__ = (
        Index("idx_email", "email"),
        Index("idx_status", "candidate_status"),
        Index("idx_city", "city"),
        Index("idx_country", "country"),
        Index("idx_state", "state"),
    )


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), primary_key=True
    )
    skill_id: Mapped[int] = Column(
        Integer, ForeignKey("skills.skill_id"), primary_key=True
    )
    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skills", back_populates="candidate_skills")


class CandidateSoftSkill(Base):
    __tablename__ = "candidate_soft_skills"
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), primary_key=True
    )
    skill_id: Mapped[int] = Column(
        Integer, ForeignKey("skills.skill_id"), primary_key=True
    )
    candidate = relationship("Candidate", back_populates="soft_skills")
    skill = relationship("Skills", back_populates="candidate_soft_skills")


class CandidateResume(Base):
    __tablename__ = "candidate_resumes"
    id: Mapped[int] = Column("resume_id", Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    attachment_url: Mapped[str] = Column(String(255), nullable=False)
    source_id: Mapped[int] = Column(
        Integer, ForeignKey("source.source_id"), nullable=False
    )
    is_default: Mapped[Boolean] = Column(Boolean, nullable=False)
    candidates = relationship("Candidate", back_populates="resumes")
    source = relationship("Source", back_populates="resumes")


class CandidateEducation(Base):
    __tablename__ = "candidate_education"
    id: Mapped[int] = Column(
        "education_id", Integer, primary_key=True, autoincrement=True
    )
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    institution: Mapped[str] = Column(String(255), nullable=False)
    degree: Mapped[str] = Column(String(255), nullable=False)
    start_date: Mapped[Date] = Column(Date)
    end_date: Mapped[Date] = Column(Date)
    aggregate: Mapped[DECIMAL] = Column(DECIMAL(5, 2))
    category: Mapped[str] = Column(
        Enum(
            "High School",
            "Military Service",
            "Vocational School",
            "Associate",
            "Pre-Bachelors",
            "Bachelors",
            "Post-Bachelors",
            "Masters",
            "Doctorate",
        ),
        nullable=False,
    )
    attachment_url: Mapped[str] = Column(String(255))
    candidates = relationship("Candidate", back_populates="education")


class CandidateWorkExperience(Base):
    __tablename__ = "candidate_work_experience"
    id: Mapped[int] = Column(
        "experience_id", Integer, primary_key=True, autoincrement=True
    )
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    employer: Mapped[str] = Column(String(255), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    start_date: Mapped[Date] = Column(Date)
    end_date: Mapped[Date] = Column(Date)
    city: Mapped[str] = Column(String(255))
    country: Mapped[str] = Column(String(255))
    state: Mapped[str] = Column(String(255))
    candidates = relationship("Candidate", back_populates="work_experiences")


class CandidateReference(Base):
    __tablename__ = "candidate_references"
    id: Mapped[int] = Column(
        "reference_id", Integer, primary_key=True, autoincrement=True
    )
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    reference_type: Mapped[str] = Column(Enum("Other", "Personal", "Professional"))
    reference_name: Mapped[str] = Column(String(255), nullable=False)
    company_name: Mapped[str] = Column(String(255))
    designation: Mapped[str] = Column(String(255), nullable=False)
    email: Mapped[str] = Column(String(255), nullable=False)
    contact_number: Mapped[str] = Column(String(20))
    candidates = relationship("Candidate", back_populates="references")


class Certification(Base):
    __tablename__ = "certification"
    id: Mapped[int] = Column(
        "certification_id", Integer, primary_key=True, autoincrement=True
    )
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    certification_name: Mapped[str] = Column(String(255), nullable=False)
    completion_date: Mapped[Date] = Column(Date)
    attachment_url: Mapped[str] = Column(String(255))
    candidates = relationship("Candidate", back_populates="certifications")


class CandidateDocument(Base):
    __tablename__ = "candidate_documents"
    id: Mapped[int] = Column(
        "document_id", Integer, primary_key=True, autoincrement=True
    )
    candidate_id: Mapped[int] = Column(
        Integer, ForeignKey("candidate.candidate_id"), nullable=False
    )
    document_name: Mapped[str] = Column(String(255), nullable=False)
    document_type: Mapped[str] = Column(String(255), nullable=False)
    document_status: Mapped[str] = Column(Enum("Active", "Inactive"), nullable=False)
    attachment_url: Mapped[str] = Column(String(255), nullable=False)
    expiry_date: Mapped[Date] = Column(Date)
    candidates = relationship("Candidate", back_populates="documents")
