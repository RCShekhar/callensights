from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, field_validator


class GetUploadsResponseModel(BaseModel):
    media_code: str
    media_type: str
    media_size: Optional[int] = 0
    media_length: Optional[int] = 0
    created_date: datetime
    user_id: str
    user_name: str
    lead_id: int
    lead_name: str
    conv_type: str

    @field_validator("created_date")
    def validate_event_date(cls, value) -> Any:
        return value.isoformat()

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')  # Customize the datetime serialization format
        }
