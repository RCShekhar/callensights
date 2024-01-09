from pydantic import BaseModel, field_validator

from datetime import datetime
from typing import List, Optional, Any, Union, Dict


class LeadConversation(BaseModel):
    user_name: str
    event_type: str
    event_info: Optional[Dict[str, Any]]
    event_date: datetime
    lead_name: str

    @field_validator("event_date")
    def validate_event_date(cls, value) -> Any:
        return value.isoformat()

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')  # Customize the datetime serialization format
        }


class LeadInfoResponse(BaseModel):
    lead_id: int
    lead_name: str
    assigned_clerk_id: Optional[str]
    country: Optional[str]
    state: Optional[str]
    email: str
    phone: str
    description: Optional[str] = None
    conversations: List[LeadConversation]
