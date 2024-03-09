from datetime import datetime

from fastapi import Depends

from app.src.core.models.db_models import AccountType
from app.src.core.repositories.account_repository import AccountRepository
from app.src.core.schemas.requests.account_request import CreateAccountRequest
from app.src.core.schemas.responses.account_response import CreateAccountResponse
from app.src.core.services.base_service import BaseService


class AccountService(BaseService):

    def __init__(self, repository: AccountRepository = Depends()):
        super().__init__("Accounts")
        self.repository = repository

    def add_account(self, user_id: str, inputs: CreateAccountRequest) -> CreateAccountResponse:
        self.repository.assume_user_exists(user_id)
        internal_user_id = self.repository.get_internal_user_id(user_id)
        account_dict = inputs.model_dump()
        workflow = account_dict['job_submission_workflow']
        account_type = account_dict['account_type']

        if not account_dict.get('account_owner'):
            account_dict['account_owner'] = internal_user_id
        account_dict['contract_start_date'] = datetime.now()
        account_dict['created_by'] = internal_user_id
        account_dict['job_submission_workflow'] = self.repository.get_workflow_id(workflow)
        account_dict['account_type'] = self.repository.get_internal_id(AccountType, 'name', account_type)

        response = self.repository.add_account(account_dict)
        return CreateAccountResponse.model_validate(response)
