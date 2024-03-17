from typing import Any

from pydantic import BaseModel, field_validator

from app.src.common.enum.background_enums import BackgroundTaskStatusEnum


class BackgroundTaskResponseModel(BaseModel):
    status: BackgroundTaskStatusEnum
    comment: str

    @field_validator("status")
    def validate_status(cls, value) -> Any:
        return value.value
