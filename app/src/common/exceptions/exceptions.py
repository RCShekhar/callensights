from typing import Optional, Dict, Any

from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException


class NoUserFoundException(BaseAppException):
    def __int__(
            self,
            description: str,
            data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = 409
        self.description = description
        self.data = data
        self.custom_error_code = CustomErrorCode.NO_SUCH_USER

        super().__init__(
            status_code=self.status_code,
            description=self.description,
            data=self.data,
            custom_error_code=self.custom_error_code
        )


class NotAssignedToUserException(BaseAppException):
    def __int__(
            self,
            description: str,
            data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = 410
        self.description = description
        self.data = data
        self.custom_error_code = CustomErrorCode.NOT_ASSIGNED_TO_USER

        super().__init__(
            status_code=self.status_code,
            description=self.description,
            data=self.data,
            custom_error_code=self.custom_error_code
        )

