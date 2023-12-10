from typing import Optional

from pydantic import BaseModel, HttpUrl, validate_email, field_validator


class UpdateUserRequest(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    role: Optional[str] = None

    @field_validator('email')
    def email_validator(cls, value):
        return validate_email(value)[-1]
