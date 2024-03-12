from typing import Dict, Any

from sqlalchemy import select

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException
from app.src.core.models.db_models import Account, JobSubmissionWorkflow, AccountType
from app.src.core.repositories.geniric_repository import GenericDBRepository


class AccountRepository(GenericDBRepository):
    def __init__(self) -> None:
        super().__init__(Account)

    @handle_db_exception
    def add_account(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        account = Account(**inputs)
        self.session.add(account)
        self.session.commit()
        return {
            'account_id': account.id,
            'account_name': account.account_name,
            'comment': "Account created successfully"
        }

    @handle_db_exception
    def get_workflow_id(self, workflow: str) -> int:
        query = select(JobSubmissionWorkflow.id.label("workflow_id")).where(
            JobSubmissionWorkflow.name == workflow.upper())
        result = self.session.execute(query).fetchone()
        if not result:
            raise BaseAppException(
                404,
                f"No such Wrokflow configuration found: {workflow}",
                CustomErrorCode.NOT_FOUND_ERROR,
                {'workflow': workflow}
            )
        return result._asdict()['workflow_id']

    @handle_db_exception
    def get_account_types_enum(self) -> Dict[str, Any]:
        query = select(AccountType.code, AccountType.name)
        results = self.session.execute(query).fetchall()
        return dict([row.tuple() for row in results])

    @handle_db_exception
    def get_internal_account_type_id(self, name: str) -> int:
        query = select(AccountType.id).filter(AccountType.name == name.upper())
        rs = self.session.execute(query).fetchone()
        if not rs:
            raise BaseAppException(
                status_code=405,
                description="Invlid or no such account type found.",
                custom_error_code=CustomErrorCode.NOT_FOUND_ERROR,
                data={'account_type': name}
            )
        type_id, _ = rs.tuple()
        return type_id
