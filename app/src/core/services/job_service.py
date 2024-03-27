from fastapi import Depends, HTTPException

from mysqlx import IntegrityError
from sqlalchemy.exc import NoResultFound
from app.src.core.models.ats.job_model import Job
from app.src.core.repositories.job_repository import JobRepository
from app.src.core.schemas.requests.job_request import CreateJobRequest
from app.src.core.schemas.responses.job_response import (
    CreateJobResponse,
    GetJobFieldValuesResponse,
)
from app.src.core.services.base_service import BaseService
from app.src.common.app_logging.logging import logger
from starlette import status


class JobService(BaseService):
    def __init__(self, repository: JobRepository = Depends()):
        super().__init__("Jobs")
        self._repository = repository

    def create_job(
        self, user_id: str, job_input: CreateJobRequest
    ) -> CreateJobResponse:
        try:
            # Ensure the user exists before proceeding
            self._repository.assume_user_exists(user_id)

            # Extract job and relation data from the input
            job_data = job_input.model_dump(exclude_unset=True)
            recruiters = job_data.pop("job_recruiters", None)
            additional_recruiters = job_data.pop("job_additional_recruiters", None)
            account_managers = job_data.pop("job_account_managers", None)
            recruitment_managers = job_data.pop("job_recruitment_managers", None)
            sourcers = job_data.pop("job_sourcers", None)
            job_primary_skills = job_data.pop("job_primary_skills", None)
            job_secondary_skills = job_data.pop("job_secondary_skills", None)

            # Start the transaction
            self._repository.session.begin()

            # Create the main job entity and related entities within a transaction
            created_job: Job = self._repository.add_job(job_data)
            self._repository.add_job_relations(
                job_id=created_job.job_id,
                recruiters=recruiters,
                additional_recruiters=additional_recruiters,
                account_managers=account_managers,
                sourcers=sourcers,
                recruitment_managers=recruitment_managers,
            )
            self._repository.map_skills_to_job(
                created_job.job_id, job_primary_skills, job_secondary_skills
            )

            # Commit the transaction if all operations are successful
            self._repository.session.commit()

            return CreateJobResponse.model_validate({"job_id": created_job.job_id})
        except IntegrityError as error:
            # Rollback the transaction in case of an IntegrityError
            self._repository.session.rollback()
            logger.error(f"Database integrity error while creating job: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create job due to a data integrity error.",
            )
        except Exception as error:
            # Rollback the transaction for any other exceptions
            self._repository.session.rollback()
            logger.error(f"Unexpected error while creating job: {error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred.",
            )

    def update_job(
        self, user_id: str, job_id: int, job_input: CreateJobRequest
    ) -> CreateJobResponse:
        self._repository.assume_user_exists(user_id)
        job = job_input.model_dump()
        recruiters = job.pop("job_recruiters", None)
        additional_recruiters = job.pop("job_additional_recruiters", None)
        account_managers = job.pop("job_account_managers", None)
        recruitment_managers = job.pop("job_recruitment_managers", None)
        sourcers = job.pop("job_sourcers", None)
        job_primary_skills = job.pop("job_primary_skills", None)
        job_secondary_skills = job.pop("job_secondary_skills", None)
        updated_job = self._repository.update_job(job_id, job)
        if not updated_job:
            logger.error(f"Job with ID {job_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found.",
            )
        self._repository.add_job_relations(
            job_id=job_id,
            recruiters=recruiters,
            additional_recruiters=additional_recruiters,
            account_managers=account_managers,
            sourcers=sourcers,
            recruitment_managers=recruitment_managers,
        )
        self._repository.map_skills_to_job(
            job_id, job_primary_skills, job_secondary_skills
        )
        logger.info(f"Job with ID {job_id} updated successfully.")
        return CreateJobResponse.model_validate({"job_id": job_id})

    def get_job(self, user_id: str, job_id: int):
        try:
            self._repository.assume_user_exists(user_id)
            job = self._repository.get_job(job_id)
            if not job:
                logger.error(f"Job with ID {job_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with ID {job_id} not found.",
                )
            return job
        except Exception as e:
            logger.error(f"Error getting job with ID {job_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting job with ID {job_id}",
            )

    def delete_job(self, user_id: str, job_id: int) -> dict:
        self._repository.assume_user_exists(user_id)
        try:
            self._repository.delete_job(job_id)
            return {"message": f"Job with ID {job_id} has been deleted."}
        except NoResultFound as e:
            logger.error(f"Job with ID {job_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found.",
            )

    def get_field_values(self, user_id: str) -> GetJobFieldValuesResponse:
        self._repository.assume_user_exists(user_id)

        job_domains = self._repository.get_job_domain_list()
        industries = self._repository.get_industry_list()
        accounts = self._repository.get_accounts_list()
        field_values = {
            "accounts": accounts,
            "industries": industries,
            "job_domains": job_domains,
        }

        return GetJobFieldValuesResponse.model_validate(field_values)
