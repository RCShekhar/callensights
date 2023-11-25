from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import AnyHttpUrl


class MediaResponse(BaseModel):
    file: Optional[str]
    media_code: Optional[str]
    presigned_url: Optional[Dict[str, Any]]
    message: Optional[str]



