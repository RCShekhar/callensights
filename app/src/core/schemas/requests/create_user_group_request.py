from typing import Optional

from pydantic import BaseModel


class CreateUserGroupRequest(BaseModel):
    group_name: str
    group_desc: Optional[str]
