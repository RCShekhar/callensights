from typing import Dict, Any

from sqlalchemy.exc import IntegrityError

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.account_model import Account
from app.src.core.repositories.geniric_repository import GenericDBRepository


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
            logger.error(f"Database integrity error while creating account: {e}", exc_info=True)
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating account: {e}", exc_info=True)
            self.session.rollback()
            raise
