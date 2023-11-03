from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import AnyHttpUrl


class MediaResponse(BaseModel):
    file: Optional[str] = Field(..., validation_alias="MEDIA_FILE")
    audio_code: Optional[str] = Field(..., validation_alias="AUDIO_CODE")
    presigned_url: Optional[AnyHttpUrl] = Field(..., validation_alias="PRESIGNED_URL")
    message: Optional[str] = Field(..., validation_alias="MESSAGE")


class UploadMediaResponseModel(BaseModel):
    response: List[Optional[MediaResponse]] = []
