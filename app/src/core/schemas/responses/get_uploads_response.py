from pydantic import BaseModel


class GetUploadsResponseModel(BaseModel):
    media_code: str
    media_type: str
    media_size: int
    media_length: int
    lead_name: str
    conv_type: str

