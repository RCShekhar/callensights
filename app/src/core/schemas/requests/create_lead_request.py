from typing import Optional
from pydantic import BaseModel


class CreateLeadRequestModel(BaseModel):
    name: str
    email: str
    phone: str
    stage_code: Optional[str] = None
    country: Optional[str] = None
    st_province: Optional[str] = None
    lead_type_code: str
