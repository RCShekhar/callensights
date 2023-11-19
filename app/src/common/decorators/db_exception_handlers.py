from functools import wraps
from typing import Callable

from sqlalchemy.exc import DatabaseError

from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.enum.custom_error_code import CustomErrorCode


def handle_db_exception(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            raise BaseAppException(
                status_code=e.code,
                description=str(e),
                custom_error_code=CustomErrorCode.DATABASE_ERROR
            )

    return wrapper
