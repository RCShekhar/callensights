from pydantic import BaseModel

from app.src.common.enum.background_enums import BackgroundTaskStatusEnum


class BackgroundTaskResponseModel(BaseModel):
    status: BackgroundTaskStatusEnum
    comment: str