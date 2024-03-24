from collections import defaultdict
from sqlalchemy import literal, select, union_all
from typing import Any, Dict, List, Optional, Type

from sqlalchemy.exc import IntegrityError, NoResultFound

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.account_model import Account
from app.src.core.models.ats.job_model import (
    Job,
    JobAccountManager,
    JobAdditionalRecruiter,
    JobRecruiter,
    JobRecruitmentManager,
    JobSourcer,
)
from app.src.core.models.ats.lookup_models import (
    Industry,
    JobDomains,
    JobPrimarySkill,
    JobSecondarySkill,
    Skills,
)
from app.src.core.models.db_models import User
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.responses.job_response import (
    SelectResponse,
)


class JobRepository(GenericDBRepository):
    def __init__(self) -> None:
        super().__init__(Job)

    def add_job(self, job: Dict[str, Any]) -> Job:
        """
        Create a new job record in the database.

        Args:
            job (Dict[str, Any]): The data for the new job.

        Returns:
            Job: The newly created job object.

        Raises:
            IntegrityError: If the job data violates database constraints.
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            job = Job(**job)
            self.session.add(job)
            self.session.commit()
            logger.info(f"Job created: {job}")
            return job
        except IntegrityError as e:
            logger.error(
                f"Database integrity error while creating job: {e}", exc_info=True
            )
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating job: {e}", exc_info=True)
            self.session.rollback()
            raise

    def update_job(self, job_id: int, job_update: Dict[str, Any]) -> Job:
        """
        Create a new job record in the database.

        Args:
            job (Dict[str, Any]): The data for the new job.

        Returns:
            Job: The newly created job object.

        Raises:
            IntegrityError: If the job data violates database constraints.
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            job = self.session.query(Job).filter(Job.job_id == job_id).first()
            if job:
                for key, value in job_update.items():
                    setattr(job, key, value)
                self.session.commit()
                self.session.refresh(job)
            return job
        except IntegrityError as e:
            logger.error(
                f"Database integrity error while creating job: {e}", exc_info=True
            )
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating job: {e}", exc_info=True)
            self.session.rollback()
            raise

    def get_job(self, job_id: int) -> Optional[Dict]:
        job_query = (
            select(
                Job,
                Industry.industry_name,
                JobDomains.domain_name,
                Account.account_name,
                User.id.label("user_id"),
                User.user_name,
            )
            .join(Industry, Industry.industry_id == Job.industry_id)
            .join(
                JobDomains,
                JobDomains.job_domain_id == Job.job_domain_id,
                isouter=True,
            )
            .join(Account, Account.account_id == Job.account_id)
            .join(JobRecruiter, JobRecruiter.job_id == Job.job_id, isouter=True)
            .join(User, User.id == JobRecruiter.recruiter_id, isouter=True)
            .where(Job.job_id == job_id)
        )
        result = self.session.execute(job_query).first()

        if not result:
            return None

        job_info, industry_name, domain_name, account_name, user_id, username = result

        primary_skills_query = (
            select(Skills.skill_name)
            .join(JobPrimarySkill, JobPrimarySkill.skill_id == Skills.skill_id)
            .where(JobPrimarySkill.job_id == job_id)
        )
        primary_skills = [
            skill[0] for skill in self.session.execute(primary_skills_query).all()
        ]

        secondary_skills_query = (
            select(Skills.skill_name)
            .join(JobSecondarySkill, JobSecondarySkill.skill_id == Skills.skill_id)
            .where(JobSecondarySkill.job_id == job_id)
        )
        secondary_skills = [
            skill[0] for skill in self.session.execute(secondary_skills_query).all()
        ]

        recruiter_query = (
            self.session.query(User.id, User.user_name, literal("recruiter"))
            .join(JobRecruiter, JobRecruiter.recruiter_id == User.id)
            .filter(JobRecruiter.job_id == job_id)
        )
        additional_recruiter_query = (
            self.session.query(User.id, User.user_name, literal("additional_recruiter"))
            .join(
                JobAdditionalRecruiter,
                JobAdditionalRecruiter.additional_recruiter_id == User.id,
            )
            .filter(JobAdditionalRecruiter.job_id == job_id)
        )
        logger.info(f"Job retrieved: {additional_recruiter_query}")
        account_manager_query = (
            self.session.query(User.id, User.user_name, literal("account_manager"))
            .join(JobAccountManager, JobAccountManager.account_manager_id == User.id)
            .filter(JobAccountManager.job_id == job_id)
        )
        sourcer_query = (
            self.session.query(User.id, User.user_name, literal("sourcer"))
            .join(JobSourcer, JobSourcer.sourcer_id == User.id)
            .filter(JobSourcer.job_id == job_id)
        )
        recruitment_manager_query = (
            self.session.query(User.id, User.user_name, literal("recruitment_manager"))
            .join(
                JobRecruitmentManager,
                JobRecruitmentManager.recruitment_manager_id == User.id,
            )
            .filter(JobRecruitmentManager.job_id == job_id)
        )

        all_users_query = union_all(
            recruiter_query,
            additional_recruiter_query,
            account_manager_query,
            sourcer_query,
            recruitment_manager_query,
        )
        all_users = self.session.execute(all_users_query).fetchall()

        logger.info(f"Job retrieved: {all_users}")

        users_dict = defaultdict(list)
        for user_id, user_name, user_type in all_users:
            users_dict[user_type].append({"id": user_id, "username": user_name})

        job_response = {
            "job_id": job_info.job_id,
            "job_status": job_info.job_status,
            "job_title": job_info.job_title,
            "customer_type": job_info.customer_type,
            "show_client_vendor_info": job_info.show_client_vendor_info,
            "publish": job_info.publish,
            "city": job_info.city,
            "country": job_info.country,
            "state": job_info.state,
            "zip_code": job_info.zip_code,
            "no_of_positions": job_info.no_of_positions,
            "target_date": job_info.target_date,
            "remote_status": job_info.remote_status,
            "qualifications": job_info.qualifications,
            "client_job_id": job_info.client_job_id,
            "salary": job_info.salary,
            "pay_billing_details": job_info.pay_billing_details,
            "job_description": job_info.job_description,
            "account": {"id": job_info.account_id, "name": account_name},
            "job_industry": {"id": job_info.industry_id, "name": industry_name},
            "job_domain": (
                {"id": job_info.job_domain_id, "name": domain_name}
                if domain_name
                else None
            ),
            "job_primary_skills": primary_skills,
            "job_secondary_skills": secondary_skills,
            "job_recruiters": users_dict["recruiter"],
            "job_additional_recruiters": users_dict["additional_recruiter"],
            "job_account_managers": users_dict["account_manager"],
            "job_sourcers": users_dict["sourcer"],
            "job_recruitment_managers": users_dict["recruitment_manager"],
        }

        return job_response

    def get_job_skills(self, job_id: int) -> List[int]:
        """
        Get the list of primary and secondary skills associated with a job.

        Args:
            job_id (int): The ID of the job.

        Returns:
            List[int]: The list of skill IDs.
        """
        primary_skills = (
            self.session.query(JobPrimarySkill.skill_id).filter_by(job_id=job_id).all()
        )
        primary_skills = [skill_id for (skill_id,) in primary_skills]

        secondary_skills = (
            self.session.query(JobSecondarySkill.skill_id)
            .filter_by(job_id=job_id)
            .all()
        )
        secondary_skills = [skill_id for (skill_id,) in secondary_skills]

        job_skills = {primary_skills, secondary_skills}

        return job_skills

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

    def map_skills_to_job(
        self, job_id: int, primary_skills: List[str], secondary_skills: List[str]
    ):
        """
        Map primary and secondary skills to a job.

        Args:
            job_id (int): The ID of the job.
            primary_skills (List[str]): The list of primary skills.
            secondary_skills (List[str]): The list of secondary skills.
        """
        for skill_name in primary_skills:
            skill_id = self.create_or_get_skill_id(skill_name)
            job_primary_skill = JobPrimarySkill(job_id=job_id, skill_id=skill_id)
            try:
                self.session.add(job_primary_skill)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

        for skill_name in secondary_skills:
            skill_id = self.create_or_get_skill_id(skill_name)
            job_secondary_skill = JobSecondarySkill(job_id=job_id, skill_id=skill_id)
            try:
                self.session.add(job_secondary_skill)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()

    def add_job_relations(
        self,
        job_id: int,
        recruiters: Optional[List[int]],
        additional_recruiters: Optional[List[int]],
        account_managers: Optional[List[int]],
        sourcers: Optional[List[int]],
        recruitment_managers: Optional[List[int]],
    ) -> None:
        try:
            job = self.session.query(Job).filter(Job.job_id == job_id).one()
            if job is None:
                logger.error(f"Job with ID {job_id} not found.")
                return None
            all_user_ids = (
                (recruiters or [])
                + (additional_recruiters or [])
                + (account_managers or [])
                + (sourcers or [])
                + (recruitment_managers or [])
            )
            users = (
                self.session.query(User.clerk_id, User.id)
                .filter(User.clerk_id.in_(all_user_ids))
                .all()
            )
            users_dict = {user.clerk_id: user.id for user in users}
            relations = {
                "recruiters": JobRecruiter,
                "additional_recruiters": JobAdditionalRecruiter,
                "account_managers": JobAccountManager,
                "sourcers": JobSourcer,
                "recruitment_managers": JobRecruitmentManager,
            }
            user_id_attr_names = {
                "recruiters": "recruiter_id",
                "additional_recruiters": "additional_recruiter_id",
                "account_managers": "account_manager_id",
                "sourcers": "sourcer_id",
                "recruitment_managers": "recruitment_manager_id",
            }
            for relation_name, relation_class in relations.items():
                relation_ids = locals()[relation_name]
                if relation_ids:
                    for user_id in relation_ids:
                        if not users_dict.get(user_id):
                            logger.error(
                                f"Failed to add {relation_name} with id {user_id} to job {job_id}: User not found in the database",
                                extra={
                                    "job_id": job_id,
                                    "user_id": user_id,
                                    "relation": relation_name,
                                },
                            )
                            continue
                        relation = relation_class(
                            job_id=job.job_id,
                            **{
                                user_id_attr_names[relation_name]: users_dict.get(
                                    user_id
                                )
                            },
                        )
                        self.session.merge(relation)

            logger.info(f"Job relations created for job id: {job_id}")
            self.session.commit()
        except NoResultFound as e:
            logger.error(f"Job or user not found: {e}", exc_info=True)
            self.session.rollback()
            raise
        except IntegrityError as e:
            logger.error(
                f"Database integrity error while creating job relations: {e}",
                exc_info=True,
            )
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error while creating job relations: {e}", exc_info=True
            )
            self.session.rollback()
            raise

    def get_industry_list(self) -> List[SelectResponse]:
        """
        Get the list of industries available in the database.

        Returns:
            List[str]: The list of industries.
        """
        industries = self.session.query(Industry).distinct().all()
        return [
            SelectResponse.model_validate(
                {"value": industry.industry_id, "label": industry.industry_name}
            )
            for industry in industries
        ]

    def get_job_domain_list(self) -> List[SelectResponse]:
        """
        Get the list of Job Domains available in the database.

        Returns:
            List[str]: The list of Job Domains.
        """
        domains = self.session.query(JobDomains).distinct().all()
        return [
            SelectResponse.model_validate(
                {"value": domain.job_domain_id, "label": domain.domain_name}
            )
            for domain in domains
        ]

    def get_accounts_list(self) -> List[SelectResponse]:
        """
        Get the list of accounts, selecting only account_id and account_name.

        Returns:
            List[Dict[str, Any]]: The list of accounts with only account_id and account_name.
        """
        accounts: List[Type[Account]] = self.session.query(
            Account.account_id, Account.account_name
        ).all()
        return [
            SelectResponse.model_validate(
                {"value": account.account_id, "label": account.account_name}
            )
            for account in accounts
        ]

    def delete_job(self, job_id: int) -> None:
        """
        Delete a job from the database.

        Args:
            job_id (int): The ID of the job to delete.
        """
        try:
            job = self.session.query(Job).filter_by(job_id=job_id).one()
            self.session.delete(job)
            self.session.commit()
            logger.info(f"Job with ID {job_id} deleted.")
        except NoResultFound:
            logger.error(f"Job with ID {job_id} not found.")
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error while deleting job: {e}", exc_info=True)
            self.session.rollback()
            raise
