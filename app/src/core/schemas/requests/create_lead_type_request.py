from pydantic import BaseModel


class CreateLeadTypeRequestModel(BaseModel):
    code: str
    name: str
    description: str
