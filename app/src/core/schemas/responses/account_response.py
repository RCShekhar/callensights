from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from app.src.core.schemas.requests.account_request import AccountType, AccountStatus, JobsSubmissionWorkflow


class CreateAccountResponse(BaseModel):
    account_id: int
    account_name: str
    account_owner: str


class AccountResponse(BaseModel):
    account_id: int
    account_name: str
    display_name: Optional[str] = None
    account_status: AccountStatus
    account_owner: str
    account_type: AccountType
    account_website: str
    industry: Optional[str] = None
    contract_end_date: Optional[date] = None
    jobs_submission_workflow: Optional[JobsSubmissionWorkflow] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    created_at: datetime
    modified_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
