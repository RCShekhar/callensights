from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CreateUserGroupResponse(BaseModel):
    id: int
    group_name: str
