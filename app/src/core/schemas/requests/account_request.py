from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.src.common.enum.account_enums import JobWorkflows


class CreateAccountRequest(BaseModel):
    account_name: str
    display_name: str
    account_owner: Optional[str] = None
    account_type: str = 'CLIENT'
    website: HttpUrl
    industry: Optional[str] = None
    job_submission_workflow: JobWorkflows