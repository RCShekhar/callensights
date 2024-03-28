from typing import List, Union

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette import status

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.candidate_model import CandidateSkill, CandidateSoftSkill
from app.src.core.repositories.candidate_repository import CandidateRepository
from app.src.core.repositories.job_repository import JobRepository
from app.src.core.schemas.requests.candidate_request import (
    CreateCandidateRequest,
    UpdateCandidateRequest,
)
from app.src.core.schemas.responses.candidate_response import (
    CandidateFormattedResponseModel,
    CreateCandidateResponse,
    GetCandidateFieldValuesResponse,
)
from app.src.core.services.base_service import BaseService


class CandidateService(BaseService):
    """
    Service for handling operations related to candidates.
    """

    def __init__(
        self,
        repository: CandidateRepository = Depends(),
        job_repository: JobRepository = Depends(),
    ):
        """
        Initialize the CandidateService with a repository for persistence.
        """
        super().__init__("Candidates")
        self._repository = repository
        self._job_repository = job_repository

    def add_candidate(self, user_id: str, inputs: CreateCandidateRequest):
        """
        Add a new candidate to the system.

        :param user_id: The ID of the user adding the candidate.
        :param inputs: The data for the new candidate.
        :return: The ID of the new candidate.
        :raises HTTPException: If there is an error adding the candidate.
        """
        self._repository.assume_user_exists(user_id)

        candidate_data = inputs.model_dump()
        internal_user_id = self._repository.get_internal_user_id(user_id)
        if internal_user_id is None:
            logger.error(f"Internal user ID for {user_id} could not be resolved.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Internal User ID could not be resolved.",
            )
        owner_id: str = candidate_data.get("owner_id")
        candidate_data["owner_id"] = self._resolve_owner_id(owner_id, internal_user_id)
        candidate_data["created_by"] = internal_user_id

        try:
            self._repository.session.begin_nested()
            candidate_id = self._repository.add_candidate(candidate_data)
            self.add_related_entities(candidate_id, inputs)
            self._repository.map_skills_to_candidate(
                candidate_id, inputs.skills, inputs.soft_skills
            )
            self._repository.session.commit()
            return CreateCandidateResponse.model_validate(
                {"candidate_id": candidate_id}
            )
        except IntegrityError as error:
            if self._is_mysql_duplicate_entry_error(error):
                logger.warning(
                    f"Conflict: Duplicate candidate name: {candidate_data.get('name')}."
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Candidate with the given name already exists.",
                )
            logger.error(
                f"Integrity error: Failed to create candidate due to a data integrity error. Error: {error}."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create candidate due to a data integrity error.",
            )
        except Exception as error:
            logger.critical(
                f"Critical Error: Unexpected error while creating candidate: {error}.",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred.",
            )

    def update_candidate(
        self,
        user_id: str,
        candidate_id: int,
        input_data: CreateCandidateRequest,
    ) -> CreateCandidateResponse:
        """
        Service method for updating an existing candidate.
        """
        self._repository.assume_user_exists(user_id)
        try:
            dump = input_data.model_dump()
            self._repository.update_candidate_and_relations(candidate_id, dump)
            return CreateCandidateResponse(candidate_id=candidate_id)
        except NoResultFound:
            raise ValueError(f"Candidate with ID {candidate_id} not found")

    def get_candidate(
        self, user_id: str, candidate_id: int, for_update: bool = False
    ) -> Union[CandidateFormattedResponseModel, UpdateCandidateRequest]:
        """
        Retrieve information about a candidate.

        :param user_id: The ID of the user retrieving the candidate.
        :param candidate_id: The ID of the candidate to retrieve.
        :return: The information about the candidate.
        :raises HTTPException: If there is an error retrieving the candidate.
        """
        try:
            self._repository.assume_user_exists(user_id)

            candidate = self._repository.get_candidate(
                candidate_id, for_update=for_update
            )
            if candidate is None:
                logger.warning(f"Candidate with ID {candidate_id} does not exist.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Candidate with ID {candidate_id} does not exist. Please check the ID and try again.",
                )

            if for_update:
                return UpdateCandidateRequest.model_validate(candidate)
            return CandidateFormattedResponseModel.model_validate(candidate)
        except NoResultFound:
            logger.error(f"Candidate with ID {candidate_id} does not exist.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} does not exist. Please check the ID and try again.",
            )

    def add_related_entities(self, candidate_id: int, inputs: CreateCandidateRequest):
        """
        Add related entities for a candidate.

        :param candidate_id: The ID of the candidate.
        :param inputs: The data for the related entities.
        """
        entities = [
            (inputs.resumes, "Resume"),
            (inputs.education_details, "Education"),
            (inputs.work_experience_details, "Work Experience"),
            (inputs.references, "Reference"),
            (inputs.certifications, "Certification"),
            (inputs.documents, "Document"),
        ]

        for entity_data, entity_name in entities:
            self._add_entities(candidate_id, entity_data, entity_name)

    def get_field_values(self, user_id: str):
        """
        Get field values for creating a new candidate.

        :param user_id: The ID of the user retrieving the field values.
        :return: The field values for creating a new candidate.
        :raises HTTPException: If there is an error retrieving the field values.
        """
        self._repository.assume_user_exists(user_id)

        try:
            source = self._repository.get_source_list()
            work_authorization = self._repository.get_work_authorization_list()
            employment_types = self._repository.get_employment_type_list()
            accounts = self._job_repository.get_accounts_list()
            field_values = {
                "source": source,
                "accounts": accounts,
                "work_authorization": work_authorization,
                "employment_types": employment_types,
            }

            return GetCandidateFieldValuesResponse.model_validate(field_values)

        except Exception as error:
            logger.error(
                f"Error getting field values for creating a new candidate: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while getting field values for creating a new candidate.",
            )

    def delete_candidate(self, user_id: str, candidate_id: int) -> None:
        """
        Delete a candidate from the system.

        :param user_id: The ID of the user deleting the candidate.
        :param candidate_id: The ID of the candidate to delete.
        :raises HTTPException: If there is an error deleting the candidate.
        """
        self._repository.assume_user_exists(user_id)

        try:
            self._repository.delete_candidate(candidate_id)
        except NoResultFound:
            logger.warning(f"Candidate with ID {candidate_id} does not exist.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} does not exist. Please check the ID and try again.",
            )
        except Exception as error:
            logger.error(f"Error deleting candidate with ID {candidate_id}: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting candidate with ID {candidate_id}.",
            )

    def _add_entities(
        self, candidate_id: int, entities: List[BaseModel], entity_name: str
    ) -> None:
        """
        Add a list of entities for a candidate.

        :param candidate_id: The ID of the candidate.
        :param entities: The entities to add.
        :param entity_name: The name of the entity type.
        """
        for entity in entities:
            entity_data = entity.model_dump()
            entity_data["candidate_id"] = candidate_id
            self._repository.add_entity(entity_name, entity_data)

    def _resolve_owner_id(self, owner_id: str, default_owner_id: str) -> str:
        """
        Resolve the account owner ID with fallback.

        :param owner_id: The owner ID to resolve.
        :param default_owner_id: The default owner ID to use if the owner ID cannot be resolved.
        :return: The resolved owner ID.
        """
        resolved_owner_id = self._repository.get_internal_user_id(owner_id)
        return resolved_owner_id if resolved_owner_id is not None else default_owner_id

    @staticmethod
    def _is_mysql_duplicate_entry_error(exception: IntegrityError) -> bool:
        """
        Check if the IntegrityError is due to a MySQL duplicate entry.

        :param exception: The exception to check.
        :return: True if the exception is due to a MySQL duplicate entry, False otherwise.
        """
        return exception.orig.args[0] == 1062
