from pydantic import BaseModel


class GetUploadsRequestModel(BaseModel):
    user_id: int
