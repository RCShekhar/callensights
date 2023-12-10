from pydantic import BaseModel

from datetime import datetime
from typing import List


class LeadConversation(BaseModel):
    media_code: str
    event_date: datetime


class LeadInfoResponse(BaseModel):
    lead_id: int
    lead_name: str
    email: str
    phone: str
    description: str
    conversations: List[LeadConversation]
