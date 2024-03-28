from datetime import date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl

from app.src.core.schemas.requests.candidate_request import (
    CertificationModel,
    SkillModel,
)
from app.src.core.schemas.responses.job_response import SelectResponse


class CreateCandidateResponse(BaseModel):
    candidate_id: int


class AddressModel(BaseModel):
    line: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]


class SocialLinkModel(BaseModel):
    linkedin_url: Optional[HttpUrl]
    twitter_url: Optional[HttpUrl]
    facebook_url: Optional[HttpUrl]
    github_url: Optional[HttpUrl]


class ExpectedRateModel(BaseModel):
    from_rate: Optional[Decimal] = Field(None, alias="from")
    to: Optional[Decimal]
    type: Optional[str]


class EmploymentDetailsModel(BaseModel):
    job_title: Optional[str]
    current_rate: Optional[Decimal]
    current_rate_type: Optional[str]
    expected_rate: ExpectedRateModel
    remote_status: Optional[str]
    willing_to_relocate: Optional[bool]
    years_of_experience: Optional[int]
    industry: Optional[str]
    employment_type: Optional[str]


class DocumentModel(BaseModel):
    document_name: str
    attachment_url: HttpUrl
    document_type: str
    document_status: str


class EducationModel(BaseModel):
    institution: str
    degree: str
    start_date: Optional[date]
    end_date: Optional[date]
    aggregate: Optional[Decimal]
    category: str
    attachment_url: Optional[HttpUrl]


class ReferenceModel(BaseModel):
    reference_type: str
    reference_name: str
    company_name: Optional[str]
    designation: str
    email: str
    contact_number: str


class CandidateSource(BaseModel):
    id: Optional[int]
    name: Optional[str]


class ResumeModel(BaseModel):
    attachment_url: HttpUrl
    source: Optional[CandidateSource]
    is_default: bool


class WorkExperienceModel(BaseModel):
    employer: str
    title: str
    start_date: Optional[date]
    end_date: Optional[date]
    city: Optional[str]
    country: Optional[str]
    state: Optional[str]


class CertificationModel(BaseModel):
    certification_name: str
    completion_date: Optional[date]
    attachment_url: Optional[HttpUrl]


class CandidateFormattedResponseModel(BaseModel):
    candidate_id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    full_name: str
    contact_name: Optional[str]
    date_of_birth: Optional[date]
    email: str
    alternate_email: Optional[str]
    phone: Optional[str]
    mobile: str
    address: AddressModel
    gender: Optional[str]
    social_links: SocialLinkModel
    video_resume: Optional[HttpUrl]
    profile_summary: Optional[str]
    employment_details: EmploymentDetailsModel
    skills: List[SkillModel]
    soft_skills: List[SkillModel]
    work_authorization: Optional[str]
    documents: List[DocumentModel]
    education: List[EducationModel]
    references: List[ReferenceModel]
    resumes: List[ResumeModel]
    work_experiences: List[WorkExperienceModel]
    certifications: List[CertificationModel]


class GetCandidateFieldValuesResponse(BaseModel):
    source: List[SelectResponse]
    work_authorization: List[SelectResponse]
    employment_types: List[SelectResponse]
    accounts: List[SelectResponse]
