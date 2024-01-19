from typing import Optional, List

from pydantic import BaseModel, field_validator
from datetime import datetime


class StageInfo(BaseModel):
    stage_id: int
    stage_name: str


class LeadPosition(BaseModel):
    lead_id: int
    lead_name: str
    stage_id: int
    assigned_to: str
    user_name: str
    modified_dt: datetime


class UserWorkspaceResponse(BaseModel):
    stages: List[StageInfo]
    leads: List[LeadPosition]
