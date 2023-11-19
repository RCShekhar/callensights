from typing import Optional, Any

from pydantic import BaseModel, validate_email, field_validator


class CreateUserRequest(BaseModel):
    user_name: Optional[str] = ""
    first_name: str
    middle_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: str
    phone: str
    organization: str
    role: str
    user_group: int

    @field_validator('email')
    def email_validation(cls, value) -> Optional[Any]:
        return validate_email(value)[-1]
