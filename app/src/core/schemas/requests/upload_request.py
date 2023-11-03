from typing import Optional

from pydantic import BaseModel, Field


class UploadMediaInputsModel(BaseModel):
    user_id: Optional[str] = Field(..., validation_alias="USER_ID")
    rep_name: Optional[str] = Field(..., validation_alias="REP_NAME")
    lead_name: Optional[str] = Field(..., validation_alias="LEAD_NAME")
    lead_type: Optional[str] = Field(..., validation_alias="LEAD_TYPE")
    conv_type: Optional[str] = Field(..., validation_alias="CONV_TYPE")
    demography: Optional[str] = Field(..., validation_alias="DEMOGRAPHY")
    lang_code: Optional[str] = Field(..., validation_alias="LANG_CODE")
    product: Optional[str] = Field(..., validation_alias="PRODUCT")
