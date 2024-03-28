from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from decimal import Decimal

from app.src.core.schemas.responses.job_response import SelectResponse


class CreateSubmissionResponse(BaseModel):
    submission_id: int


class SubmissionDocumentModel(BaseModel):
    id: int
    attachment_url: str


class SubmissionNoteModel(BaseModel):
    id: int
    note_type: str
    note: str
    file_url: Optional[str] = None


class SubmissionAdditionalRecipientsModel(BaseModel):
    id: int
    email: EmailStr


class GetSubmissionResponse(BaseModel):
    submission_id: int
    job_id: int
    candidate_id: int
    availability: datetime
    bill_rate: Optional[Decimal] = None
    pay_rate: Decimal
    additional_recipients: Optional[List[EmailStr]] = None
    notes: Optional[str] = []
    created_at: datetime
    modified_at: datetime
    deleted_at: Optional[datetime] = None
    pay_type: SelectResponse
    engagement_type: SelectResponse
    documents: List[SubmissionDocumentModel] = []
    notes: List[SubmissionNoteModel] = []
    additional_recipients: List[SubmissionAdditionalRecipientsModel] = []


class BaseResponse(BaseModel):
    message: str
