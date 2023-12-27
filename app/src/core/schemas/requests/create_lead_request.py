from typing import Optional
from pydantic import BaseModel


class CreateLeadRequestModel(BaseModel):
    name: str
    email: str
    phone: str
    stage_code: str
    country: Optional[str]
    st_province: Optional[str]
    lead_type_code: str
