from json import dumps
from typing import Union, Dict, Any
from collections import defaultdict

from app.src.common.enum.custom_error_code import CustomErrorCode


class BaseAppException(Exception):
    def __init__(
            self,
            status_code: int,
            description: str,
            custom_error_code: CustomErrorCode,
            data: Union[None, Dict[str, Any]] = None
    ):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.description = description
        self.data = defaultdict(str, data) if data is not None else defaultdict(str)
        self.custom_error_code = custom_error_code.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exception_case": self.exception_case,
            "status_code": self.status_code,
            "description": self.description,
            "data": self.data,
            "custom_error_code": self.custom_error_code
        }

