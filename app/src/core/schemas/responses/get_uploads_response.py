from typing import Optional

from pydantic import BaseModel


class GetUploadsResponseModel(BaseModel):
    media_code: str
    media_type: str
    media_size: Optional[int] = 0
    media_length: Optional[int] = 0
    lead_name: str
    conv_type: str

