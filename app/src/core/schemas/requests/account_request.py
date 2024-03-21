from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AccountStatus(str, Enum):
    active = 'Active'
    inactive = 'Inactive'


class AccountType(str, Enum):
    client = 'Client'


class JobsSubmissionWorkflow(str, Enum):
    vendor = 'Vendor'
    prime_vendor = 'Prime Vendor'
    direct_client = 'Direct Client'


class CreateAccountRequest(BaseModel):
    account_name: str
    display_name: Optional[str] = None
    account_status: AccountStatus
    account_owner: Optional[str] = None
    account_type: Optional[AccountType] = AccountType.client
    account_website: str
    industry: Optional[str] = None
    contract_end_date: Optional[date] = None
    jobs_submission_workflow: Optional[JobsSubmissionWorkflow] = None
