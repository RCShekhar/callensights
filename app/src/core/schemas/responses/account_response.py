from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from app.src.core.schemas.requests.account_request import (
    AccountType,
    AccountStatus,
    JobsSubmissionWorkflow,
)


class CreateAccountResponse(BaseModel):
    account_id: int
    account_name: str
    account_owner: str


class AccountUser(BaseModel):
    user_id: str
    username: str


class GetAccountResponse(BaseModel):
    account_id: int
    account_name: str
    display_name: Optional[str] = None
    account_status: AccountStatus
    account_owner: AccountUser
    account_type: Optional[AccountType] = AccountType.client
    account_website: str
    industry: Optional[str] = None
    contract_end_date: Optional[date] = None
    jobs_submission_workflow: Optional[JobsSubmissionWorkflow] = None
    created_by: Optional[AccountUser] = None
    modified_by: Optional[AccountUser] = None
    created_at: datetime
    modified_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class UpdateAccountResponse(BaseModel):
    account_id: int

    class Config:
        from_attributes = True


class DeleteAccountResponse(BaseModel):
    account_id: int

    class Config:
        from_attributes = True
