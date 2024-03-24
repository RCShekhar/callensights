from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class JobStatusEnum(str, Enum):
    draft = 'Draft'
    active = 'Active'
    closed_won = 'Closed WON'
    closed = 'Closed'
    on_hold = 'On Hold'
    cancelled = 'Cancelled'
    target_date = 'Target Date'
    expired = 'Expired'


class CustomerTypeEnum(str, Enum):
    internal = 'Internal'
    vendor = 'Vendor'
    prime_vendor = 'Prime Vendor'
    direct_client = 'Direct Client'


class RemoteStatusEnum(str, Enum):
    on_site = 'On Site'
    remote = 'Remote'
    hybrid = 'Hybrid'


class QualificationsEnum(str, Enum):
    high_school = 'High School'
    military_service = 'Military Service'
    associate = 'Associate'
    pre_bachelors = 'Pre Bachelors'
    bachelors = 'Bachelors'
    post_bachelors = 'Post Bachelors'
    masters = 'Masters'
    doctorate = 'Doctorate'


class CreateJobRequest(BaseModel):
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

    account_id: int
    industry_id: int
    job_description: Optional[str] = None
    job_domain_id: Optional[int] = None
    
    job_primary_skills: Optional[List[str]]
    job_secondary_skills: Optional[List[str]]

    job_recruiters: Optional[List[str]] = None
    job_additional_recruiters: Optional[List[str]] = None
    job_account_managers: Optional[List[str]] = None
    job_sourcers: Optional[List[str]] = None
    job_recruitment_managers: Optional[List[str]] = None

    class Config:
        use_enum_values = True
