from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.account_model import Account
from app.src.core.repositories.account_repository import AccountRepository
from app.src.core.schemas.requests.account_request import CreateAccountRequest
from app.src.core.schemas.responses.account_response import CreateAccountResponse
from app.src.core.services.base_service import BaseService


class AccountService(BaseService):
    def __init__(self, repository: AccountRepository = Depends()):
        super().__init__("Accounts")
        self._repository = repository

    def add_account(self, user_id: str, inputs: CreateAccountRequest) -> CreateAccountResponse:
        self._repository.assume_user_exists(user_id)

        account_data = inputs.model_dump()
        internal_user_id = self._repository.get_internal_user_id(user_id)

        if internal_user_id is None:
            logger.error(f"Internal user ID for {user_id} could not be resolved.")
            raise HTTPException(status_code=status.HTTP_500_BAD_REQUEST,
                                detail="Internal User ID could not be resolved.")

        owner_id = account_data.get("account_owner", internal_user_id)
        account_data["account_owner"] = self._resolve_account_owner(owner_id, internal_user_id)
        account_data["created_by"] = internal_user_id

        try:
            created_account: Account = self._repository.add_account(account_data)
            return CreateAccountResponse.model_validate(
                {
                    "account_id": created_account.account_id,
                    "account_name": created_account.account_name,
                    "account_owner": created_account.account_owner
                }
            )
        except IntegrityError as error:
            if self._is_mysql_duplicate_entry_error(error):
                logger.error(f"Duplicate account name: {account_data.get('account_name')}.")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Account with this name already exists.")
            logger.error(f"Database integrity error while creating account: {error}.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Failed to create account due to a data integrity error.")
        except Exception as error:
            logger.error(f"Unexpected error while creating account: {error}.", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred.")

    def _resolve_account_owner(self, owner_id: str, default_owner_id: str) -> str:
        """Resolve the account owner ID with fallback."""
        resolved_owner_id = self._repository.get_internal_user_id(owner_id)
        return resolved_owner_id if resolved_owner_id is not None else default_owner_id

    @staticmethod
    def _is_mysql_duplicate_entry_error(exception: IntegrityError) -> bool:
        """Check if the IntegrityError is due to a MySQL duplicate entry."""
        return exception.orig.args[0] == 1062
