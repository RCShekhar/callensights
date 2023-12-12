from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator

from app.src.common.constants.global_constants import ALLOWED_TYPES


class UploadMediaInputsModel(BaseModel):
    user_id: str
    rep_name: Optional[str] = ""
    lead_id: int
    conv_type: str
    demography: Optional[str]
    lang_code: Optional[str]
    product: Optional[str]
    files: Optional[List[str]]

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

