from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette import status
from app.src.common.app_logging.logging import logger
from app.src.core.repositories.submission_repository import SubmissionRepository
from app.src.core.schemas.requests.submission_request import (
    CreateSubmissionRequest,
    UpdateSubmissionRequest,
)
from app.src.core.schemas.responses.submission_response import (
    CreateSubmissionResponse,
    GetSubmissionResponse,
)
from app.src.core.services.base_service import BaseService


class SubmissionService(BaseService):
    def __init__(self, repository: SubmissionRepository = Depends()):
        super().__init__("Submissions")
        self._repository = repository

    def create_submission(
        self, user_id: str, submission_data: CreateSubmissionRequest
    ) -> dict:
        try:
            self._repository.assume_user_exists(user_id)

            if self._repository.does_submission_combination_exist(
                job_id=submission_data.job_id, candidate_id=submission_data.candidate_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A submission for this candidate and job combination already exists.",
                )

            submission_id: int = self._repository.add_submission(submission_data)

            logger.info(
                f"Submission created successfully for user ID {user_id}. Submission ID: {submission_id}."
            )
            return {"submission_id": submission_id}
        except HTTPException as he:
            raise he
        except IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission creation failed due to a database integrity issue.",
            )
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified user does not exist.",
            )
        except Exception as error:
            logger.critical(
                f"Unexpected error while creating submission: {error}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during submission creation.",
            )

    def get_submission(
        self, user_id: str, submission_id: int, for_update: bool = False
    ):
        try:
            self._repository.assume_user_exists(user_id)
            submission = self._repository.get_submission(submission_id, for_update)
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The specified submission does not exist.",
                )
            return GetSubmissionResponse.model_validate(submission)
        except HTTPException as he:
            raise he
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified submission does not exist.",
            )
        except Exception as error:
            logger.critical(
                f"Unexpected error while getting submission: {error}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while getting submission.",
            )

    def update_submission(
        self,
        user_id: str,
        submission_id: int,
        submission_input: UpdateSubmissionRequest,
    ):
        try:
            self._repository.assume_user_exists(user_id)
            submission = self._repository.does_submission_exist(submission_id)
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The specified submission does not exist.",
                )
            dump = submission_input.model_dump()
            self._repository.update_submission(submission_id, dump)
            return {
                "message": f"Submission with ID {submission_id} has been updated successfully."
            }
        except HTTPException as he:
            raise he
        except IntegrityError as error:
            if "1452" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Submission update failed due to a foreign key constraint violation. Please ensure the referenced data exists.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission update failed due to a database integrity issue.",
            )
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified submission does not exist.",
            )
        except Exception as error:
            logger.critical(
                f"Unexpected error while updating submission: {error}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating submission.",
            )

    def delete_submission(self, user_id: str, submission_id: int):
        try:
            self._repository.assume_user_exists(user_id)
            submission = self._repository.does_submission_exist(submission_id)
            logger.info(
                f"User with ID - {user_id} attempting to delete submission with ID - {submission_id}."
            )
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The specified submission does not exist.",
                )
            self._repository.delete_submission(submission_id)
            logger.info(
                f"User with ID - {user_id} has deleted submission with ID - {submission_id}."
            )
            return {
                "message": f"Submission with ID {submission_id} has been deleted successfully."
            }
        except HTTPException as he:
            raise he
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified submission does not exist.",
            )
        except Exception as error:
            logger.critical(
                f"Unexpected error while deleting submission: {error}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting submission.",
            )
