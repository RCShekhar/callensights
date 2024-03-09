from typing import Dict, Any

from sqlalchemy import select

from app.src.common.decorators.db_exception_handlers import handle_db_exception
from app.src.core.models.db_models import Account, JobSubmissionWorkflow
from app.src.core.repositories.geniric_repository import GenericDBRepository


class AccountRepository(GenericDBRepository):
    @handle_db_exception
    def add_account(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        account = Account(**inputs)
        self.session.add(account)
        self.session.commit()
        return {'account_id': account.id, 'account_name': account.account_name}

    @handle_db_exception
    def get_workflow_id(self, workflow: str) -> int:
        query = select(JobSubmissionWorkflow.id.label("workflow_id")).where(
            JobSubmissionWorkflow.name == workflow.upper())
        result = self.session.execute(query).fetchone()
        return result._asdict()['workflow_id']
