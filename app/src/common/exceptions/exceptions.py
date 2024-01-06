from typing import Optional, Dict, Any

from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException


class NoUserFoundException(BaseAppException):
    def __init__(
            self,
            data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = 409
        self.description = "Invalid user or No such user found"
        self.data = data
        self.custom_error_code = CustomErrorCode.NO_SUCH_USER

        super().__init__(
            status_code=self.status_code,
            description=self.description,
            data=self.data,
            custom_error_code=self.custom_error_code
        )


class NoLeadFoundException(BaseAppException):
    def __init__(
            self,
            data: Optional[Dict[str, Any]]
    ):
        self.status_code = 408
        self.description = "Invalid Lead or No such lead found"
        self.data = data
        self.custom_error_code = CustomErrorCode.NO_SUCH_LEAD

        super().__init__(
            status_code=self.status_code,
            description=self.description,
            data=self.data,
            custom_error_code=self.custom_error_code
        )


class NotAssignedToUserException(BaseAppException):
    def __init__(
            self,
            data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = 410
        self.description = "Media not assigned to user"
        self.data = data
        self.custom_error_code = CustomErrorCode.NOT_ASSIGNED_TO_USER

        super().__init__(
            status_code=self.status_code,
            description=self.description,
            data=self.data,
            custom_error_code=self.custom_error_code
        )


class InvalidMediaException(BaseAppException):
    def __init__(
            self,
            description: str,
            data: Optional[Dict[str, Any]]
    ):
        self.status_code = 411
        self.description = "Invalid or No such media exists"
        self.data = data
        self.custom_error_code = CustomErrorCode.INVALID_MEDIA

        super().__init__(
            status_code=self.status_code,
            description=self.description,
            data=self.data,
            custom_error_code=self.custom_error_code
        )
