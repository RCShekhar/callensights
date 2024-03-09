from pydantic import BaseModel


class CreateAccountResponse(BaseModel):
    account_code: str
    account_name: str
    comment: str