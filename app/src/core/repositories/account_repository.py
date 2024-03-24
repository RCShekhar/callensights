from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import aliased

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.account_model import Account
from app.src.core.models.db_models import User
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.requests.account_request import UpdateAccountRequest
from app.src.core.schemas.responses.account_response import UpdateAccountResponse


class AccountRepository(GenericDBRepository):
    def __init__(self) -> None:
        super().__init__(Account)

    def add_account(self, account_data: Dict[str, Any]) -> Account:
        """
        Create a new account record in the database.

        Args:
            account_data (Dict[str, Any]): The data for the new account.

        Returns:
            Account: The newly created account object.

        Raises:
            IntegrityError: If the account data violates database constraints.
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            account = Account(**account_data)
            self.session.add(account)
            self.session.commit()
            logger.info(f"Account created: {account}")
            return account
        except IntegrityError as e:
            logger.error(
                f"Database integrity error while creating account: {e}", exc_info=True
            )
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating account: {e}", exc_info=True)
            self.session.rollback()
            raise

    def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an account record from the database.

        Args:
            account_id (int): The ID of the account to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The account details if found, None otherwise.
        """
        CreatedByUser = aliased(User)
        UpdatedByUser = aliased(User)
        try:
            stmt = (
                select(
                    Account.account_id,
                    Account.account_name,
                    Account.display_name,
                    Account.account_status,
                    Account.account_type,
                    Account.account_website,
                    Account.industry,
                    Account.contract_end_date,
                    Account.jobs_submission_workflow,
                    User.clerk_id.label("owner_user_id"),
                    User.user_name.label("owner_username"),
                    CreatedByUser.clerk_id.label("created_by_user_id"),
                    CreatedByUser.user_name.label("created_by_username"),
                    UpdatedByUser.clerk_id.label("updated_by_user_id"),
                    UpdatedByUser.user_name.label("updated_by_username"),
                    Account.created_at,
                    Account.modified_at,
                    Account.deleted_at,
                )
                .join(User, User.id == Account.account_owner)
                .join(UpdatedByUser, isouter=True)
                .join(CreatedByUser, isouter=True)
                .where(Account.account_id == account_id)
            )

            row = self.session.execute(stmt).first()

            return row._asdict() if row else None

        except Exception as e:
            logger.error(f"Error while fetching account: {e}", exc_info=True)
            raise

    def update_account(
        self, account_id: int, account_data: dict[str, Any]
    ) -> Optional[UpdateAccountResponse]:
        """
        Update an existing account record in the database.

        Args:
            account_id (int): The ID of the account to update.
            account_data (UpdateAccountRequest): The updated account data.

        Returns:
            Optional[UpdateAccountResponse]: The updated account object, or None if the account is not found.

        Raises:
            IntegrityError: If the account data violates database constraints.
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            account = (
                self.session.query(Account)
                .filter(Account.account_id == account_id)
                .one_or_none()
            )

            if account:
                for key, value in account_data.items():
                    setattr(account, key, value)

                self.session.commit()
                self.session.refresh(account)
                return account
            else:
                logger.warning(f"Account with ID {account_id} not found.")
                return None
        except IntegrityError as e:
            logger.error(
                f"Database integrity error while updating account: {e}", exc_info=True
            )
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error while updating account: {e}", exc_info=True)
            self.session.rollback()
            raise

    def delete_account(self, account_id: int) -> bool:
        """
        Delete an account record from the database.

        Args:
            account_id (int): The ID of the account to delete.

        Returns:
            Optional[int]: The ID of the deleted account, or None if the account was not found.

        Raises:
            IntegrityError: If the account data violates database constraints.
            Exception: If an unexpected error occurs during the operation.
        """
        if not isinstance(account_id, int):
            raise TypeError("account_id must be an integer")

        try:
            account = (
                self.session.query(Account)
                .filter(Account.account_id == account_id)
                .one_or_none()
            )

            if account:
                self.session.delete(account)
                self.session.commit()
                logger.info(f"Account with ID {account_id} deleted successfully.")
                return True
            else:
                logger.warning(f"Account with ID {account_id} not found.")
                return False
        except NoResultFound as e:
            logger.error(
                f"Failed to delete account with ID {account_id}: Account not found",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.session.rollback()
            raise
        except IntegrityError as e:
            logger.error(
                f"Failed to delete account with ID {account_id}: Database integrity error",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(
                f"Failed to delete account with ID {account_id}: Unexpected error",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.session.rollback()
            raise

    def is_authorized_to_update_or_delete(
        self, internal_user_id: int, account_id: int
    ) -> bool:
        """
        Check if the user is authorized to update or delete the account.
        """
        if not isinstance(internal_user_id, int):
            raise ValueError("Internal user ID must be an integer.")

        account = (
            self.session.query(
                Account.account_owner, Account.created_by, Account.account_id
            )
            .filter(Account.account_id == account_id)
            .one_or_none()
        )

        # Check if the account exists and the user is the account owner or the creator of the account
        return (
            account
            and int(account.account_owner) == internal_user_id
            or int(account.created_by) == internal_user_id
        )
