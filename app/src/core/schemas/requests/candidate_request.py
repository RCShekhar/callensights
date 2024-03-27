from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel

from app.src.core.models.ats.candidate_model import Candidate


class SkillModel(BaseModel):
    id: int
    name: str


class CandidateStatusEnum(str, Enum):
    available = "Available"
    not_available = "Not Available"
    do_not_call = "Do Not Call"
    blacklist = "Blacklist"
    inactive = "Inactive"
    placed = "Placed"
    unsubscribe = "Unsubscribe"


class StatusEnum(str, Enum):
    active = "Active"
    inactive = "Inactive"


class RemoteStatusEnum(str, Enum):
    remote = "Remote"
    on_site = "On Site"
    hybrid = "Hybrid"
    any = "Any"


class RateTypeEnum(str, Enum):
    hourly = "Hourly"
    daily = "Daily"
    weekly = "Weekly"
    monthly = "Monthly"
    salary = "Salary"


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class ReferenceTypeEnum(str, Enum):
    professional = "Professional"
    personal = "Personal"
    other = "Other"


class CategoryEnum(str, Enum):
    high_school = "High School"
    military_service = "Military Service"
    vocational_school = "Vocational School"
    associate = "Associate"
    pre_bachelors = "Pre-Bachelors"
    bachelors = "Bachelors"
    post_bachelors = "Post-Bachelors"
    masters = "Masters"
    doctorate = "Doctorate"


class CandidateResumeModel(BaseModel):
    attachment_url: str
    source_id: int
    is_default: bool


class CandidateResumeCompleteModel(CandidateResumeModel, BaseModel):
    source: Optional[Dict[str, Union[int, str]]] = None


class CandidateEducationModel(BaseModel):
    institution: str
    degree: str
    start_date: date
    end_date: Optional[date] = None
    aggregate: Optional[Decimal] = None
    category: CategoryEnum
    attachment_url: Optional[str] = None


class CandidateWorkExperienceModel(BaseModel):
    employer: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None


class CandidateReferenceModel(BaseModel):
    reference_type: ReferenceTypeEnum
    reference_name: str
    company_name: Optional[str] = None
    designation: str
    email: str
    contact_number: str


class CertificationModel(BaseModel):
    certification_name: str
    completion_date: date
    attachment_url: Optional[str] = None


class CandidateDocumentModel(BaseModel):
    document_name: str
    document_type: str
    document_status: StatusEnum
    attachment_url: str
    expiry_date: Optional[date] = None


class CandidateModel(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    phone: Optional[str] = None
    mobile: str
    date_of_birth: Optional[date] = None
    candidate_status: CandidateStatusEnum
    owner_id: int
    job_title: Optional[str] = None
    authorization_id: int
    source_id: Optional[int] = None
    years_of_experience: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    zip_code: Optional[str] = None
    profile_summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    video_resume: Optional[str] = None
    security_clearance: Optional[bool] = None
    willing_to_relocate: Optional[bool] = None
    employment_type_id: int
    account_id: int
    contact_name: Optional[str] = None
    expected_rate_from: Optional[Decimal] = None
    expected_rate_to: Optional[Decimal] = None
    expected_rate_type: Optional[RateTypeEnum] = None
    current_rate_type: Optional[RateTypeEnum] = None
    remote_status: RemoteStatusEnum
    gender: GenderEnum
    current_rate: Optional[Decimal] = None
    language_id: Optional[int] = None
    github_url: Optional[str] = None
    alternate_email: Optional[str] = None
    industry_id: int

    class Meta:
        orm_model = Candidate


class CreateCandidateRequest(CandidateModel, BaseModel):
    skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    resumes: List[CandidateResumeModel] = []
    education_details: List[CandidateEducationModel] = []
    work_experience_details: List[CandidateWorkExperienceModel] = []
    references: List[CandidateReferenceModel] = []
    certifications: List[CertificationModel] = []
    documents: List[CandidateDocumentModel] = []

    class Config:
        from_attributes = True


class SkillModel(BaseModel):
    id: Optional[int] = None
    name: str


class CandidateModelWithId(BaseModel):
    candidate_id: int


class UpdateCandidateResumeModel(CandidateResumeModel):
    id: Optional[int] = None


class UpdateCandidateEducationModel(CandidateEducationModel):
    id: Optional[int] = None


class UpdateCandidateWorkExperienceModel(CandidateWorkExperienceModel):
    id: Optional[int] = None


class UpdateCandidateReferenceModel(CandidateReferenceModel):
    id: Optional[int] = None


class UpdateCertificationModel(CertificationModel):
    id: Optional[int] = None


class UpdateCandidateDocumentModel(CandidateDocumentModel):
    id: Optional[int] = None


class UpdateCandidateRequest(CandidateModel, CandidateModelWithId, BaseModel):
    skills: Optional[List[SkillModel]] = None
    soft_skills: Optional[List[SkillModel]] = None
    resumes: List[UpdateCandidateResumeModel] = []
    education_details: List[UpdateCandidateEducationModel] = []
    work_experience_details: List[UpdateCandidateWorkExperienceModel] = []
    references: List[UpdateCandidateReferenceModel] = []
    certifications: List[UpdateCertificationModel] = []
    documents: List[UpdateCandidateDocumentModel] = []

    class Config:
        from_attributes = True
