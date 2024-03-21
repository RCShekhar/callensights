from enum import Enum

from app.src.core.repositories.account_repository import AccountRepository


class JobWorkflowsEnum(str, Enum):
    VENDOR: str = "VENDOR"
    PRIME_VENDOR: str = "PRIME_VENDOR"
    DIRECT_CLIENT: str = "DIRECT_CLIENT"


account_repository = AccountRepository()
AccountTypesEnum = Enum('AccountTypesEnum', account_repository.get_account_types_enum())
