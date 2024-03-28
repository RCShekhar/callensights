from datetime import date
from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal


class SubmissionDocumentModel(BaseModel):
    attachment_url: str


class UpdateSubmissionDocumentModel(SubmissionDocumentModel, BaseModel):
    id: Optional[int] = None


class NoteTypeEnum(str, Enum):
    call = "Call"
    meeting = "Meeting"
    notes = "Notes"
    others = "Others"


class SubmissionNoteModel(BaseModel):
    note_type: NoteTypeEnum
    note: str
    file_url: Optional[str] = None


class UpdateSubmissionNoteModel(SubmissionNoteModel, BaseModel):
    id: Optional[int] = None


class UpdateSubmissionAdditionalRecipients(BaseModel):
    id: Optional[int] = None
    email: EmailStr


class SubmissionModel(BaseModel):
    job_id: int
    candidate_id: int
    availability: date
    engagement_type_id: int
    pay_type_id: int
    bill_rate: Optional[Decimal] = None
    pay_rate: Decimal


class CreateSubmissionRequest(SubmissionModel, BaseModel):
    additional_recipients: Optional[List[EmailStr]] = None
    documents: Optional[List[SubmissionDocumentModel]] = None
    notes: Optional[List[SubmissionNoteModel]] = None


class SubmissionModelWithId(SubmissionModel, BaseModel):
    id: Optional[int] = None


class UpdateSubmissionRequest(SubmissionModel, BaseModel):
    additional_recipients: Optional[List[UpdateSubmissionAdditionalRecipients]] = None
    documents: Optional[List[UpdateSubmissionDocumentModel]] = None
    notes: Optional[List[UpdateSubmissionNoteModel]] = None
