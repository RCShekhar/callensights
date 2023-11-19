
from typing import Optional, Any

from pydantic import BaseModel


class BaseService:
    service_name: str

    def __init__(self, name: str = None) -> None:
        self.service_name = name


