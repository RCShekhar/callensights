from pydantic import BaseModel


class CreateAccountResponseModel(BaseModel):
    account_id: str
    account_name: str
    comment: str