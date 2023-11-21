
from pydantic import BaseModel


class CreateLeadResponseModel(BaseModel):
    lead_id: int
