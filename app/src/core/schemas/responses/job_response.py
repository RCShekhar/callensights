from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.src.core.schemas.requests.job_request import (
    CustomerTypeEnum,
    JobStatusEnum,
    QualificationsEnum,
    RemoteStatusEnum,
)


class CreateJobResponse(BaseModel):
    job_id: int


class SelectResponse(BaseModel):
    value: int
    label: str


class GetJobFieldValuesResponse(BaseModel):
    accounts: List[SelectResponse]
    industries: List[SelectResponse]
    job_domains: List[SelectResponse]


class JobUser(BaseModel):
    user_id: str
    username: str


class JobField(BaseModel):
    id: int
    name: str


class GetJobResponse(BaseModel):
    job_id: int
    job_status: JobStatusEnum
    job_title: str
    customer_type: CustomerTypeEnum
    show_client_vendor_info: Optional[bool] = None
    publish: Optional[bool] = True
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    no_of_positions: Optional[int] = None
    target_date: Optional[date] = None
    remote_status: RemoteStatusEnum
    qualifications: QualificationsEnum
    client_job_id: Optional[str] = None
    salary: Optional[Decimal] = None
    pay_billing_details: Optional[str] = None
    job_description: Optional[str] = None

    account: JobField
    job_industry: JobField
    job_domain: Optional[JobField] = None
    
    job_primary_skills: List[str]
    job_secondary_skills: List[str]

    job_recruiters: List[JobUser]
    job_additional_recruiters: List[JobUser]
    job_account_managers: List[JobUser]
    job_sourcers: List[JobUser]
    job_recruitment_managers: List[JobUser]

    class Config:
        use_enum_values = True
