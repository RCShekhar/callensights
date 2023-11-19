from pydantic import BaseModel


class CreateUserResponse(BaseModel):
    user_id: int
