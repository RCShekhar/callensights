from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator

from app.src.core.schemas.responses.lead_info_response import AssignedUser


class OverallMetricsModel(BaseModel):
    metric_name: str
    rating: int | float


class MonthlyUploadsModel(BaseModel):
    month: str
    calls_uploaded: int = 0


class RecentCallsModel(BaseModel):
    media_code: str
    lead_id: int
    lead_name: str
    stage_id: int
    assigned_to: AssignedUser
    created_dt: datetime

    @field_validator("created_dt")
    def validate_event_date(cls, value) -> Any:
        return value.isoformat()

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')  # Customize the datetime serialization format
        }