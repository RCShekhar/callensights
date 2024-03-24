from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.account_model import Account
from app.src.core.repositories.account_repository import AccountRepository
from app.src.core.schemas.requests.account_request import (
    CreateAccountRequest,
    UpdateAccountRequest,
)
from app.src.core.schemas.responses.account_response import (
    CreateAccountResponse,
    GetAccountResponse,
    UpdateAccountResponse,
)
from app.src.core.services.base_service import BaseService


class AccountService(BaseService):
    def __init__(self, repository: AccountRepository = Depends()):
        super().__init__("Accounts")
        self._repository = repository

    def add_account(
        self, user_id: str, inputs: CreateAccountRequest
    ) -> CreateAccountResponse:
        self._repository.assume_user_exists(user_id)

        account_data = inputs.model_dump()
        internal_user_id = self._repository.get_internal_user_id(user_id)

        if internal_user_id is None:
            logger.error(f"Internal user ID for {user_id} could not be resolved.")
            raise HTTPException(
                status_code=status.HTTP_500_BAD_REQUEST,
                detail="Internal User ID could not be resolved.",
            )

        owner_id = account_data.get("account_owner", internal_user_id)
        account_data["account_owner"] = self._resolve_account_owner(
            owner_id, internal_user_id
        )
        account_data["created_by"] = internal_user_id

        try:
            created_account: Account = self._repository.add_account(account_data)
            return CreateAccountResponse.model_validate(
                {
                    "account_id": created_account.account_id,
                    "account_name": created_account.account_name,
                    "account_owner": created_account.account_owner,
                }
            )
        except IntegrityError as error:
            if self._is_mysql_duplicate_entry_error(error):
                logger.error(
                    f"Duplicate account name: {account_data.get('account_name')}."
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Account with this name already exists.",
                )
            logger.error(f"Database integrity error while creating account: {error}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account due to a data integrity error.",
            )
        except Exception as error:
            logger.error(
                f"Unexpected error while creating account: {error}.", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred.",
            )

    def get_account(self, user_id: str, account_id: int) -> GetAccountResponse:
        self._repository.assume_user_exists(user_id)

        account = self._repository.get_account(account_id)

        if account is None:
            logger.error(f"Account with ID {account_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found."
            )

        account["account_owner"] = {
            "user_id": account.pop("owner_user_id"),
            "username": account.pop("owner_username"),
        }
        account["created_by"] = (
            {
                "user_id": account.pop("created_by_user_id"),
                "username": account.pop("created_by_username"),
            }
            if account.get("created_by_user_id")
            else None
        )
        account["modified_by"] = (
            {
                "user_id": account.pop("modified_by_user_id"),
                "username": account.pop("modified_by_username"),
            }
            if account.get("modified_by_user_id")
            else None
        )

        return GetAccountResponse.model_validate(account)

    def update_account(
        self, user_id: str, account_id: int, inputs: UpdateAccountRequest
    ) -> UpdateAccountResponse:
        self._repository.assume_user_exists(user_id)
        current_user_internal_id = self._repository.get_internal_user_id(user_id)
        if not (
            self._repository.is_authorized_to_update_or_delete(
                current_user_internal_id, account_id
            )
            or self._repository.is_admin(user_id)
        ):
            logger.error(
                f"User {user_id} is not authorized to update account {account_id}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this account.",
            )

        account_data = inputs.model_dump(exclude_unset=True)
        account_data["modified_by"] = current_user_internal_id

        if account_data.get("account_owner"):
            owner_id = account_data["account_owner"]
            owner_internal_user_id = self._repository.get_internal_user_id(owner_id)
            if owner_internal_user_id is None:
                logger.error(
                    f"Internal user ID for account owner {owner_id} could not be resolved."
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid account owner ID.",
                )
            account_data["account_owner"] = owner_internal_user_id

        try:
            updated_account: Optional[UpdateAccountResponse] = (
                self._repository.update_account(account_id, account_data)
            )
            return UpdateAccountResponse.model_validate(
                {"account_id": updated_account.account_id}
            )
        except IntegrityError as error:
            if self._is_mysql_duplicate_entry_error(error):
                logger.error(
                    f"Duplicate account name: {account_data.get('account_name')}."
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Account with this name already exists.",
                )
            logger.error(f"Database integrity error while updating account: {error}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update account due to a data integrity error.",
            )
        except Exception as error:
            logger.error(
                f"Unexpected error while updating account: {error}.", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred.",
            )

    def delete_account(self, user_id: str, account_id: int) -> None:
        self._repository.assume_user_exists(user_id)
        current_user_internal_id = self._repository.get_internal_user_id(user_id)
        if not (
            self._repository.is_authorized_to_update_or_delete(
                current_user_internal_id, account_id
            )
            or self._repository.is_admin(user_id)
        ):
            logger.error(
                f"User {user_id} is not authorized to delete account {account_id}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this account.",
            )

        try:
            is_deleted = self._repository.delete_account(account_id)
            if not is_deleted:
                logger.warning(f"Account with ID {account_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Account not found."
                )
        except Exception as error:
            logger.error(
                f"Unexpected error while deleting account: {error}.", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred.",
            )

    def _resolve_account_owner(self, owner_id: str, default_owner_id: str) -> str:
        """Resolve the account owner ID with fallback."""
        resolved_owner_id = self._repository.get_internal_user_id(owner_id)
        return resolved_owner_id if resolved_owner_id is not None else default_owner_id

    @staticmethod
    def _is_mysql_duplicate_entry_error(exception: IntegrityError) -> bool:
        """Check if the IntegrityError is due to a MySQL duplicate entry."""
        return exception.orig.args[0] == 1062
