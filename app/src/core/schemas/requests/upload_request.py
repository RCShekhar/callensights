from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator

from app.src.common.constants.global_constants import ALLOWED_TYPES


class UploadMediaInputsModel(BaseModel):
    user_id: int = Field(..., validation_alias="USER_ID")
    rep_name: Optional[str] = Field(..., validation_alias="REP_NAME")
    lead_id: int = Field(..., validation_alias="LEAD_ID")
    conv_type: str = Field(..., validation_alias="CONV_TYPE")
    demography: Optional[str] = Field(..., validation_alias="DEMOGRAPHY")
    lang_code: Optional[str] = Field(..., validation_alias="LANG_CODE")
    product: Optional[str] = Field(..., validation_alias="PRODUCT")
    files: Optional[List[str]] = Field(..., validation_alias="FILES")

    @classmethod
    @field_validator('files')
    def validate_files(cls, value):
        # if isinstance(value, )
        if type(value) is not list:
            raise ValueError(f"FILES must be an ordered collection")

        for file in value:
            extension = file.split('.')[-1]
            if extension.lower() not in ALLOWED_TYPES:
                raise ValueError(f"Invalid Media file")

        return value

