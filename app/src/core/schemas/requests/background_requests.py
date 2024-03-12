from pydantic import BaseModel

from app.src.common.enum.background_enums import BackgroundStageEnum


class BackgroundTaskRequestModel(BaseModel):
    media_code: str
    media_file: str
    media_bucket: str
    media_size: int
    media_length: float
    stage: BackgroundStageEnum
