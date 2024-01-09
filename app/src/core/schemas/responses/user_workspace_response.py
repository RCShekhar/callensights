from typing import Optional, List, Any

from pydantic import BaseModel


class StageInfo(BaseModel):
    stage_id: int
    stage_name: str


class LeadPosition(BaseModel):
    lead_id: int
    lead_name: str
    stage_id: int
    assigned_to: str
    user_name: str


class UserWorkspaceResponse(BaseModel):
    stages: List[StageInfo]
    leads: List[LeadPosition]
