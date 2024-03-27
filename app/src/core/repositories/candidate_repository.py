from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload
from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.candidate_model import (
    Candidate,
    CandidateDocument,
    CandidateEducation,
    CandidateReference,
    CandidateResume,
    CandidateSkill,
    CandidateSoftSkill,
    CandidateWorkExperience,
    Certification,
)
from app.src.core.models.ats.lookup_models import (
    EmploymentType,
    Skills,
    Source,
    WorkAuthorization,
)
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.requests.candidate_request import (
    CandidateModel,
    SkillModel,
    UpdateCandidateRequest,
)
from app.src.core.schemas.responses.candidate_response import (
    CandidateFormattedResponseModel,
)
from app.src.core.schemas.responses.job_response import SelectResponse


class CandidateRepository(GenericDBRepository):
    """
    Repository for handling operations related to candidates.
    Inherits from GenericDBRepository to use common database operations.
    """

    ENTITY_MODELS_DICT = {
        "Candidate": Candidate,
        "Resume": CandidateResume,
        "Education": CandidateEducation,
        "Work Experience": CandidateWorkExperience,
        "Reference": CandidateReference,
        "Certification": Certification,
        "Document": CandidateDocument,
    }

    def __init__(self) -> None:
        """
        Initialize the CandidateRepository with the Candidate model.
        """
        super().__init__(Candidate)

    def update_or_insert_related_entities(
        self, entity_class: Type, entities_data: List[dict], candidate_id: int
    ):
        """
        Generic function to update or insert related entities for a candidate.
        It identifies entities to be updated or inserted based on the presence or absence of 'id' in the entity data.
        """
        existing_entity_ids = [
            entity_data["id"] for entity_data in entities_data if "id" in entity_data
        ]
        # Remove entities not present in the update_data
        if existing_entity_ids:
            self.session.query(entity_class).filter(
                entity_class.candidate_id == candidate_id,
                entity_class.id.notin_(existing_entity_ids),
            ).delete(synchronize_session=False)
        else:
            self.session.query(entity_class).filter_by(
                candidate_id=candidate_id
            ).delete(synchronize_session=False)

        for entity_data in entities_data:
            if "id" in entity_data and entity_data["id"]:
                entity = (
                    self.session.query(entity_class)
                    .filter_by(id=entity_data["id"], candidate_id=candidate_id)
                    .one_or_none()
                )
                if entity:
                    for key, value in entity_data.items():
                        setattr(entity, key, value)
            else:
                entity_data.pop("id", None)  # Remove 'id' key if it's there
                new_entity = entity_class(**entity_data, candidate_id=candidate_id)
                self.session.add(new_entity)

    def update_or_insert_entities(
        self, entity_class: Type, entities_data: List[Dict], candidate_id: int
    ):
        """
        Generic function to update or insert entities, managing removal of not included entities.
        """
        # Fetch current entity IDs for the candidate
        current_entities = (
            self.session.query(entity_class).filter_by(candidate_id=candidate_id).all()
        )
        current_entity_ids = {entity.id for entity in current_entities}

        updated_entity_ids = set()
        for entity_data in entities_data:
            entity_id = entity_data.get("id")
            if entity_id:
                if entity_id in current_entity_ids:
                    self.session.query(entity_class).filter_by(id=entity_id).update(
                        entity_data
                    )
                    updated_entity_ids.add(entity_id)
                else:
                    logger.warning(
                        f"Entity ID {entity_id} not found among current entities. Ignoring."
                    )
            else:
                # Insert new entity
                new_entity = entity_class(**entity_data, candidate_id=candidate_id)
                self.session.add(new_entity)

        # Delete entities not in the updated list
        entities_to_delete = current_entity_ids - updated_entity_ids
        if entities_to_delete:
            self.session.query(entity_class).filter(
                entity_class.id.in_(entities_to_delete)
            ).delete(synchronize_session="fetch")

    def update_candidate_and_relations(
        self, candidate_id: int, update_data: Dict[str, Any]
    ):
        """
        Updates a candidate and its related entities, handling both updates and inserts.
        """
        try:
            candidate = (
                self.session.query(Candidate)
                .filter(Candidate.candidate_id == candidate_id)
                .one_or_none()
            )
            if not candidate:
                raise NoResultFound(f"No candidate found for ID {candidate_id}")
            logger.info(f"Updating candidate {candidate_id}")

            for key, value in CandidateModel(**update_data).model_dump().items():
                if hasattr(candidate, key):
                    setattr(candidate, key, value)

            entities_mapping = {
                "resumes": CandidateResume,
                "education_details": CandidateEducation,
                "work_experience_details": CandidateWorkExperience,
                "references": CandidateReference,
                "certifications": Certification,
                "documents": CandidateDocument,
                # "skills": CandidateSkill,
                # "soft_skills": CandidateSoftSkill,
            }
            for entity_key, entity_model in entities_mapping.items():
                entity_data = update_data.get(entity_key, None)
                logger.info(
                    f"Updating {entity_key} for candidate {candidate_id} with {entity_data}"
                )
                if entity_data is not None:
                    self.update_or_insert_entities(
                        entity_model, entity_data, candidate_id
                    )

            self._update_candidate_skills(
                candidate_id, [skill.get("name") for skill in update_data.get("skills")]
            )
            self._update_candidate_skills(
                candidate_id,
                [skill.get("name") for skill in update_data.get("skills")],
                is_soft_skill=True,
            )
            self.session.commit()

            self.session.commit()
            logger.info(
                f"Candidate {candidate_id} and related entities updated successfully."
            )
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Integrity error updating candidate {candidate_id}: {e}")
            if "unique constraint" in str(e):
                raise ValueError("Unique constraint violated") from e
            else:
                raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating candidate {candidate_id}: {e}")
            raise Exception(
                f"An error occurred while updating candidate and relations: {e}"
            ) from e

    def add_candidate(self, candidate_data_dict: Dict[str, Any]) -> int:
        """
        Add a new candidate to the database.
        """
        return self._add_entity(
            Candidate, CandidateModel(**candidate_data_dict).model_dump(), "Candidate"
        )

    def get_candidate(
        self, candidate_id: int, for_update: bool = False
    ) -> Optional[Union[CandidateFormattedResponseModel, UpdateCandidateRequest]]:
        """
        Get a candidate's information by ID.
        """
        base_query = self.session.query(Candidate).options(
            joinedload(Candidate.owner),
            joinedload(Candidate.work_authorization),
            joinedload(Candidate.source),
            joinedload(Candidate.employment_type),
            joinedload(Candidate.account),
            joinedload(Candidate.languages_known),
            joinedload(Candidate.industry),
            joinedload(Candidate.documents),
            joinedload(Candidate.education),
            joinedload(Candidate.references),
            joinedload(Candidate.resumes).joinedload(CandidateResume.source),
            joinedload(Candidate.work_experiences),
            joinedload(Candidate.certifications),
            joinedload(Candidate.skills).joinedload(CandidateSkill.skill),
            joinedload(Candidate.soft_skills).joinedload(CandidateSoftSkill.skill),
        )

        candidate = base_query.filter(Candidate.candidate_id == candidate_id).first()

        if not candidate:
            return None

        if for_update:
            return self._format_candidate_data_for_update(candidate)
        else:
            return self._format_candidate_data(candidate)

    def delete_candidate(self, candidate_id: int) -> bool:
        """
        Delete an existing candidate by ID.
        """
        try:
            candidate = (
                self.session.query(Candidate).filter_by(candidate_id=candidate_id).one()
            )
            self.session.delete(candidate)
            self.session.commit()
            logger.info(f"Candidate with ID {candidate_id} deleted successfully.")
            return True
        except NoResultFound:
            self.session.rollback()
            logger.error(f"No candidate found with ID {candidate_id} to delete.")
            raise ValueError(f"No candidate found with ID {candidate_id} to delete.")
        except Exception as general_exception:
            self.session.rollback()
            logger.error(
                f"Unexpected error while deleting candidate: {general_exception}",
                exc_info=True,
            )
            raise ValueError(
                "An unexpected error occurred while deleting the candidate."
            ) from general_exception

    def get_source_list(self) -> List[SelectResponse]:
        """
        Get the list of source available in the database.

        Returns:
            List[str]: The list of sources.
        """
        sources = self.session.query(Source).distinct().all()
        return [
            SelectResponse.model_validate(
                {"value": source.source_id, "label": source.source_name}
            ).model_dump()
            for source in sources
        ]

    def get_work_authorization_list(self) -> List[SelectResponse]:
        """
        Get the list of work authorizations available in the database.

        Returns:
            List[str]: The list of work authorizations.
        """
        work_authorizations = self.session.query(WorkAuthorization).distinct().all()
        return [
            SelectResponse.model_validate(
                {"value": wa.authorization_id, "label": wa.authorization_name}
            ).model_dump()
            for wa in work_authorizations
        ]

    def get_employment_type_list(self) -> List[SelectResponse]:
        """
        Get the list of employment types available in the database.

        Returns:
            List[str]: The list of employment types.
        """
        employment_types = self.session.query(EmploymentType).distinct().all()
        return [
            SelectResponse.model_validate(
                {"value": et.type_id, "label": et.type_name}
            ).model_dump()
            for et in employment_types
        ]

    def add_entity(self, entity_name_str: str, entity_data_dict: Dict[str, Any]) -> int:
        """
        Add a new entity related to a candidate to the database.
        """
        model = self.ENTITY_MODELS_DICT.get(entity_name_str)
        if not model:
            raise ValueError(f"Invalid entity name: {entity_name_str}")
        return self._add_entity(model, entity_data_dict, entity_name_str)

    def _add_entity(
        self, model: BaseModel, data_dict: Dict[str, Any], entity_name_str: str
    ) -> int:
        """
        Generic method to add an entity to the database.
        """
        try:
            entity = model(**data_dict)
            self.session.add(entity)
            self.session.commit()
            try:
                entity_id = getattr(entity, f"{entity_name_str.lower()}_id")
                logger.info(
                    f"{entity_name_str} added successfully with ID: {entity_id}"
                )
                return entity_id
            except AttributeError:
                logger.error(f"Invalid field value for {entity_name_str}")
                return None
        except IntegrityError as integrity_error:
            logger.error(
                f"Database integrity error while adding {entity_name_str}: {integrity_error.orig}",
                exc_info=True,
            )
            self.session.rollback()
            raise ValueError(
                f"Failed to add {entity_name_str} due to a data integrity issue."
            ) from integrity_error
        except Exception as general_exception:
            logger.error(
                f"Unexpected error while adding {entity_name_str}: {general_exception}",
                exc_info=True,
            )
            self.session.rollback()
            raise ValueError(
                f"An unexpected error occurred while adding the {entity_name_str}."
            ) from general_exception

    def map_skills_to_candidate(
        self, candidate_id: int, primary_skills: List[str], secondary_skills: List[str]
    ):
        """
        Map primary and secondary skills to a candidate.

        Args:
            candidate_id (int): The ID of the candidate.
            primary_skills (List[str]): The list of primary skills.
            secondary_skills (List[str]): The list of secondary skills.
        """
        for skill_name in primary_skills:
            skill_id = self.create_or_get_skill_id(skill_name)
            candidate_skill = CandidateSkill(
                candidate_id=candidate_id, skill_id=skill_id
            )
            try:
                self.session.add(candidate_skill)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

        for skill_name in secondary_skills:
            skill_id = self.create_or_get_skill_id(skill_name)
            candidate_soft_skill = CandidateSoftSkill(
                candidate_id=candidate_id, skill_id=skill_id
            )
            try:
                self.session.add(candidate_soft_skill)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def create_or_get_skill_id(self, skill_name: str) -> int:
        """
        Create a new skill or get the ID if it already exists.

        Args:
            skill_name (str): The name of the skill.

        Returns:
            int: The skill ID.
        """
        try:
            existing_skill = (
                self.session.query(Skills).filter_by(skill_name=skill_name).first()
            )
            if existing_skill:
                return existing_skill.skill_id
            else:
                new_skill = Skills(skill_name=skill_name)
                self.session.add(new_skill)
                self.session.commit()
                return new_skill.skill_id
        except IntegrityError:
            self.session.rollback()
            existing_skill = (
                self.session.query(Skills).filter_by(skill_name=skill_name).first()
            )
            return existing_skill.skill_id

    def get_source_list(self) -> List[SelectResponse]:
        """
        Get the list of source available in the database.

        Returns:
            List[str]: The list of sources.
        """
        sources = self.session.query(Source).distinct().all()
        return [
            SelectResponse.model_validate(
                {"value": source.source_id, "label": source.source_name}
            ).model_dump()
            for source in sources
        ]

    def _format_candidate_data(
        self, candidate: Dict[str, Any]
    ) -> CandidateFormattedResponseModel:
        """
        Format the candidate's data to reduce redundancy and improve order.
        """
        formatted_data = {
            "candidate_id": candidate.candidate_id,
            "first_name": candidate.first_name,
            "middle_name": getattr(candidate, "middle_name", ""),
            "last_name": candidate.last_name,
            "contact_name": getattr(candidate, "contact_name", None),
            "full_name": f"{candidate.first_name} {getattr(candidate, 'middle_name', '')} {candidate.last_name}".strip(),
            "date_of_birth": (
                str(candidate.date_of_birth) if candidate.date_of_birth else None
            ),
            "email": candidate.email,
            "alternate_email": getattr(candidate, "alternate_email", None),
            "phone": getattr(candidate, "phone", None),
            "mobile": candidate.mobile,
            "address": {
                "line": getattr(candidate, "address", None),
                "city": getattr(candidate, "city", None),
                "state": getattr(candidate, "state", None),
                "zip_code": getattr(candidate, "zip_code", None),
                "country": getattr(candidate, "country", None),
            },
            "gender": candidate.gender if candidate.gender else "Not Specified",
            "social_links": {
                "linkedin_url": getattr(candidate, "linkedin_url", None),
                "twitter_url": getattr(candidate, "twitter_url", None),
                "facebook_url": getattr(candidate, "facebook_url", None),
                "github_url": getattr(candidate, "github_url", None),
            },
            "video_resume": getattr(candidate, "video_resume", None),
            "profile_summary": getattr(candidate, "profile_summary", None),
            "employment_details": {
                "job_title": getattr(candidate, "job_title", None),
                "current_rate": getattr(candidate, "current_rate", None),
                "current_rate_type": getattr(candidate, "current_rate_type", None),
                "expected_rate": {
                    "from": getattr(candidate, "expected_rate_from", None),
                    "to": getattr(candidate, "expected_rate_to", None),
                    "type": getattr(candidate, "expected_rate_type", None),
                },
                "remote_status": getattr(candidate, "remote_status", "Not Specified"),
                "willing_to_relocate": (
                    candidate.willing_to_relocate
                    if candidate.willing_to_relocate is not None
                    else False
                ),
                "years_of_experience": getattr(candidate, "years_of_experience", 0),
                "industry": (
                    getattr(candidate.industry, "industry_name", None)
                    if candidate.industry
                    else None
                ),
                "employment_type": (
                    getattr(candidate.employment_type, "type_name", None)
                    if candidate.employment_type
                    else None
                ),
            },
            "skills": [
                {"id": skill.skill.skill_id, "name": skill.skill.skill_name}
                for skill in getattr(candidate, "skills", [])
            ],
            "soft_skills": [
                {"id": soft_skill.skill.skill_id, "name": soft_skill.skill.skill_name}
                for soft_skill in getattr(candidate, "soft_skills", [])
            ],
            "work_authorization": (
                getattr(candidate.work_authorization, "authorization_name", None)
                if candidate.work_authorization
                else None
            ),
            "documents": [
                {
                    "document_name": doc.document_name,
                    "attachment_url": doc.attachment_url,
                    "document_type": doc.document_type,
                    "document_status": doc.document_status,
                }
                for doc in getattr(candidate, "documents", [])
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "start_date": str(edu.start_date) if edu.start_date else None,
                    "end_date": str(edu.end_date) if edu.end_date else None,
                    "aggregate": edu.aggregate,
                    "category": edu.category,
                    "attachment_url": getattr(edu, "attachment_url", None),
                }
                for edu in getattr(candidate, "education", [])
            ],
            "references": [
                {
                    "reference_type": ref.reference_type,
                    "reference_name": ref.reference_name,
                    "company_name": getattr(ref, "company_name", None),
                    "designation": ref.designation,
                    "email": ref.email,
                    "contact_number": ref.contact_number,
                }
                for ref in getattr(candidate, "references", [])
            ],
            "resumes": [
                {
                    "attachment_url": resume.attachment_url,
                    "source": {
                        "id": getattr(resume.source, "source_id", None),
                        "name": getattr(resume.source, "source_name", None),
                    },
                    "is_default": resume.is_default,
                }
                for resume in getattr(candidate, "resumes", [])
            ],
            "work_experiences": [
                {
                    "employer": exp.employer,
                    "title": exp.title,
                    "start_date": str(exp.start_date) if exp.start_date else None,
                    "end_date": str(exp.end_date) if exp.end_date else None,
                    "city": getattr(exp, "city", None),
                    "country": getattr(exp, "country", None),
                    "state": getattr(exp, "state", None),
                }
                for exp in getattr(candidate, "work_experiences", [])
            ],
            "certifications": [
                {
                    "certification_name": cert.certification_name,
                    "completion_date": (
                        str(cert.completion_date) if cert.completion_date else None
                    ),
                    "attachment_url": getattr(cert, "attachment_url", None),
                }
                for cert in getattr(candidate, "certifications", [])
            ],
        }

        return CandidateFormattedResponseModel(**formatted_data)

    def _update_candidate_skills(
        self, candidate_id: int, skills_data: List[str], is_soft_skill: bool = False
    ):
        """
        Update or insert skills and soft skills for a candidate.

        Args:
        candidate_id (int): ID of the candidate.
        skill_ids (List[int]): List of skill IDs to associate with the candidate.
        is_soft_skill (bool): Flag to indicate if the skills are soft skills. Defaults to False.
        """

        if is_soft_skill:
            ExistingSkillModel = CandidateSoftSkill
            relation = "candidate_soft_skills"
        else:
            ExistingSkillModel = CandidateSkill
            relation = "candidate_skills"

        # Fetch and map existing skills by skill_name for quick lookup
        existing_skills = (
            self.session.query(ExistingSkillModel)
            .filter(ExistingSkillModel.candidate_id == candidate_id)
            .all()
        )
        existing_skills_map = {
            skill.skill.skill_name: skill for skill in existing_skills
        }

        # Determine skills to add
        skill_names_to_add = [
            skill_name
            for skill_name in skills_data
            if skill_name not in existing_skills_map
        ]

        # Add new skills
        for skill_name in skill_names_to_add:
            skill = (
                self.session.query(Skills)
                .filter(Skills.skill_name == skill_name)
                .one_or_none()
            )
            if skill is None:
                # Skill does not exist, create a new one
                skill = Skills(skill_name=skill_name)
                self.session.add(skill)
                self.session.flush()  # Ensure the new skill has an ID
            new_skill_relation = ExistingSkillModel(
                candidate_id=candidate_id, skill_id=skill.skill_id
            )
            getattr(skill, relation).append(new_skill_relation)
            self.session.add(new_skill_relation)

        # Determine skills to remove
        skill_names_to_remove = [
            skill_name
            for skill_name in existing_skills_map
            if skill_name not in skills_data
        ]
        for skill_name in skill_names_to_remove:
            skill_to_remove = existing_skills_map[skill_name]
            self.session.delete(skill_to_remove)

    def _format_candidate_data_for_update(
        self, candidate: Candidate
    ) -> UpdateCandidateRequest:
        formatted_data = {
            "candidate_id": candidate.candidate_id,
            "first_name": candidate.first_name,
            "middle_name": candidate.middle_name,
            "last_name": candidate.last_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "mobile": candidate.mobile,
            "date_of_birth": candidate.date_of_birth,
            "candidate_status": candidate.candidate_status,
            "owner_id": candidate.owner_id,
            "job_title": candidate.job_title,
            "authorization_id": candidate.authorization_id,
            "source_id": candidate.source_id,
            "years_of_experience": candidate.years_of_experience,
            "city": candidate.city,
            "country": candidate.country,
            "state": candidate.state,
            "address": candidate.address,
            "zip_code": candidate.zip_code,
            "profile_summary": candidate.profile_summary,
            "linkedin_url": candidate.linkedin_url,
            "twitter_url": candidate.twitter_url,
            "facebook_url": candidate.facebook_url,
            "video_resume": candidate.video_resume,
            "security_clearance": candidate.security_clearance,
            "willing_to_relocate": candidate.willing_to_relocate,
            "employment_type_id": candidate.employment_type_id,
            "account_id": candidate.account_id,
            "contact_name": candidate.contact_name,
            "expected_rate_from": candidate.expected_rate_from,
            "expected_rate_to": candidate.expected_rate_to,
            "expected_rate_type": candidate.expected_rate_type,
            "current_rate_type": candidate.current_rate_type,
            "remote_status": candidate.remote_status,
            "gender": candidate.gender,
            "current_rate": candidate.current_rate,
            "language_id": candidate.language_id,
            "github_url": candidate.github_url,
            "alternate_email": candidate.alternate_email,
            "industry_id": candidate.industry_id,
            "skills": [
                {"id": skill.skill.skill_id, "name": skill.skill.skill_name}
                for skill in candidate.skills
            ],
            "soft_skills": [
                {"id": soft_skill.skill.skill_id, "name": soft_skill.skill.skill_name}
                for soft_skill in candidate.soft_skills
            ],
            "work_authorization": (
                getattr(candidate.work_authorization, "authorization_name", None)
                if candidate.work_authorization
                else None
            ),
            "documents": [
                {
                    "id": doc.id,
                    "document_name": doc.document_name,
                    "document_type": doc.document_type,
                    "attachment_url": doc.attachment_url,
                    "document_status": doc.document_status,
                }
                for doc in getattr(candidate, "documents", [])
            ],
            "education_details": [
                {
                    "id": edu.id,
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "start_date": str(edu.start_date) if edu.start_date else None,
                    "end_date": str(edu.end_date) if edu.end_date else None,
                    "aggregate": edu.aggregate,
                    "category": edu.category,
                    "attachment_url": getattr(edu, "attachment_url", None),
                }
                for edu in getattr(candidate, "education", [])
            ],
            "references": [
                {
                    "id": ref.id,
                    "reference_type": ref.reference_type,
                    "reference_name": ref.reference_name,
                    "company_name": getattr(ref, "company_name", None),
                    "designation": ref.designation,
                    "email": ref.email,
                    "contact_number": ref.contact_number,
                }
                for ref in getattr(candidate, "references", [])
            ],
            "resumes": [
                {
                    "id": resume.id,
                    "attachment_url": resume.attachment_url,
                    "source_id": getattr(resume.source, "source_id", None),
                    "is_default": resume.is_default,
                }
                for resume in getattr(candidate, "resumes", [])
            ],
            "work_experience_details": [
                {
                    "id": exp.id,
                    "employer": exp.employer,
                    "title": exp.title,
                    "start_date": str(exp.start_date) if exp.start_date else None,
                    "end_date": str(exp.end_date) if exp.end_date else None,
                    "city": getattr(exp, "city", None),
                    "country": getattr(exp, "country", None),
                    "state": getattr(exp, "state", None),
                }
                for exp in getattr(candidate, "work_experiences", [])
            ],
            "certifications": [
                {
                    "id": cert.id,
                    "certification_name": cert.certification_name,
                    "completion_date": (
                        str(cert.completion_date) if cert.completion_date else None
                    ),
                    "attachment_url": getattr(cert, "attachment_url", None),
                }
                for cert in getattr(candidate, "certifications", [])
            ],
        }
        return UpdateCandidateRequest(**formatted_data)
