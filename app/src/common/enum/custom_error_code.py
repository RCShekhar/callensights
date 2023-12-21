from enum import Enum

class CustomErrorCode(Enum):
    AWS_ERROR = "AWS_ERROR_001"
    DATABASE_ERROR = "DATABASE_ERROR_001"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR_001"
    DUPLICATE_RESOURCE_ERROR = "DUPLICATE_RESOURCE_ERROR_001"
    AUTHORIZATION_ERROR = "JWT_AUTHORIZATION_ERROR_001"
    UNKNOWN_ERROR = "UNKNOWN_ERROR_001"