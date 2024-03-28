from typing import Dict, Any, Optional, Type

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload

from app.src.common.app_logging.logging import logger
from app.src.core.models.ats.submission_model import (
    Submission,
    SubmissionAdditionalRecipients,
    SubmissionDocument,
    SubmissionNote,
)
from app.src.core.repositories.geniric_repository import GenericDBRepository
from app.src.core.schemas.requests.submission_request import (
    CreateSubmissionRequest,
    SubmissionModel,
)


class SubmissionRepository(GenericDBRepository):
    def __init__(self) -> None:
        super().__init__(Submission)

    def add_submission(self, submission_data: CreateSubmissionRequest) -> int:
        try:
            submission_dict = submission_data.model_dump(exclude_unset=True)
            documents = submission_dict.pop("documents", [])
            notes = submission_dict.pop("notes", [])
            additional_recipients = submission_dict.pop("additional_recipients", [])

            # Create and add the submission
            submission = Submission(**submission_dict)
            self.session.add(submission)

            # Get the submission_id without committing transaction
            self.session.flush()

            # Process documents
            for document_data in documents:
                document = SubmissionDocument(
                    submission_id=submission.submission_id, **document_data
                )
                self.session.add(document)

            # Process notes
            for note_data in notes:
                note = SubmissionNote(
                    submission_id=submission.submission_id, **note_data
                )
                self.session.add(note)

            # Process Additional Recipients
            for recipient in additional_recipients:
                recipient = SubmissionAdditionalRecipients(
                    submission_id=submission.submission_id, email=recipient
                )
                self.session.add(recipient)

            self.session.commit()
            return submission.submission_id
        except IntegrityError as e:
            self.session.rollback()
            logger.error(
                f"Failed to add submission due to integrity error: {e}", exc_info=True
            )
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error in add_submission: {e}", exc_info=True)
            raise

    def does_submission_combination_exist(self, job_id: int, candidate_id: int) -> bool:
        try:
            return self.session.query(
                self.session.query(Submission)
                .filter_by(job_id=job_id, candidate_id=candidate_id)
                .exists()
            ).scalar()
        except NoResultFound:
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error in does_submission_combination_exist: {e}",
                exc_info=True,
            )
            raise

    def get_submission(
        self, submission_id: int, for_update: bool = False
    ) -> Optional[Dict[str, Any]]:
        base_query = self.session.query(Submission).options(
            joinedload(Submission.pay_type),
            joinedload(Submission.engagement_type),
            joinedload(Submission.documents),
            joinedload(Submission.notes),
            joinedload(Submission.additional_recipients),
        )
        submission = base_query.filter(
            Submission.submission_id == submission_id
        ).first()

        if not submission:
            return None

        if for_update:
            return self._format_submission_data_for_update(submission)
        else:
            return self._format_submission_data(submission)

    def does_submission_exist(self, submission_id: int) -> bool:
        """
        Check if a submission exists in the database.
        """
        try:
            return (
                self.session.query(Submission)
                .filter_by(submission_id=submission_id)
                .exists()
            ) is not None
        except NoResultFound:
            return False
        except Exception as unexpected_error:
            logger.critical(
                f"Unexpected error in `does_submission_exist` for `submission_id` {submission_id}: {unexpected_error}",
                exc_info=True,
            )
            raise

    def update_submission(self, submission_id: int, submission_data: Dict[str, Any]):
        try:
            documents = submission_data.pop("documents", [])
            notes = submission_data.pop("notes", [])
            additional_recipients = submission_data.pop("additional_recipients", [])

            submission = (
                self.session.query(Submission)
                .filter(Submission.submission_id == submission_id)
                .one_or_none()
            )

            if not submission:
                raise NoResultFound(f"No Submission found for ID {submission_id}")

            for key, value in SubmissionModel(**submission_data).model_dump().items():
                logger.info(f"Setting {key} to {value}")
                if hasattr(submission, key):
                    logger.info(f"HASATTR: Setting {key} to {value}")
                    setattr(submission, key, value)

            for document in documents:
                if "id" in document:
                    document_id = document.pop("id")
                    self.session.query(SubmissionDocument).filter_by(
                        document_id=document_id
                    ).update(document)
                else:
                    self.session.add(
                        SubmissionDocument(submission_id=submission_id, **document)
                    )

            for note in notes:
                if "id" in note:
                    note_id = note.pop("id")
                    self.session.query(SubmissionNote).filter_by(
                        note_id=note_id
                    ).update(note)
                else:
                    self.session.add(
                        SubmissionNote(submission_id=submission_id, **note)
                    )

            for recipient in additional_recipients:
                if "id" in recipient:
                    recipient_id = recipient.pop("id")
                    self.session.query(SubmissionAdditionalRecipients).filter_by(
                        submission_additional_recipients_id=recipient_id
                    ).update(recipient)
                else:
                    self.session.add(
                        SubmissionAdditionalRecipients(
                            submission_id=submission_id, **recipient
                        )
                    )

            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            logger.error(
                f"Failed to update submission due to integrity error: {e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error in update_submission: {e}", exc_info=True)
            raise

    def _format_submission_data_for_update(
        self, submission: Type[Submission]
    ) -> Dict[str, Any]:
        formatted_data = {
            "submission_id": submission.submission_id,
            "job_id": submission.job_id,
            "candidate_id": submission.candidate_id,
            "availability": submission.availability,
            "bill_rate": getattr(submission, "bill_rate", None),
            "pay_rate": submission.pay_rate,
            "additional_recipients": [
                recipient.email
                for recipient in getattr(submission, "additional_recipients", [])
            ],
            "notes": submission.notes,
            "pay_type": {
                "value": submission.pay_type.pay_type_id,
                "label": submission.pay_type.pay_type_name,
            },
            "engagement_type": {
                "value": submission.engagement_type.engagement_type_id,
                "label": submission.engagement_type.engagement_type_name,
            },
            "documents": [
                {
                    "id": document.document_id,
                    "attachment_url": document.attachment_url,
                }
                for document in getattr(submission, "documents", [])
            ],
            "notes": [
                {
                    "id": note.note_id,
                    "note_type": note.note_type,
                    "note": note.note,
                    "file_url": getattr(note, "file_url", None),
                }
                for note in getattr(submission, "notes", [])
            ],
            "additional_recipients": [
                {
                    "id": recipient.submission_additional_recipients_id,
                    "email": recipient.email,
                }
                for recipient in getattr(submission, "additional_recipients", [])
            ],
        }
        return formatted_data

    def _format_submission_data(self, submission: Type[Submission]) -> Dict[str, Any]:
        formatted_data = {
            "submission_id": submission.submission_id,
            "job_id": submission.job_id,
            "candidate_id": submission.candidate_id,
            "availability": submission.availability,
            "bill_rate": getattr(submission, "bill_rate", None),
            "pay_rate": submission.pay_rate,
            "additional_recipients": [
                recipient.email
                for recipient in getattr(submission, "additional_recipients", [])
            ],
            "notes": submission.notes,
            "created_at": submission.created_at,
            "modified_at": submission.modified_at,
            "deleted_at": getattr(submission, "deleted_at", None),
            "pay_type": {
                "value": submission.pay_type.pay_type_id,
                "label": submission.pay_type.pay_type_name,
            },
            "engagement_type": {
                "value": submission.engagement_type.engagement_type_id,
                "label": submission.engagement_type.engagement_type_name,
            },
            "documents": [
                {
                    "id": document.document_id,
                    "attachment_url": document.attachment_url,
                }
                for document in getattr(submission, "documents", [])
            ],
            "notes": [
                {
                    "id": note.note_id,
                    "note_type": note.note_type,
                    "note": note.note,
                    "file_url": getattr(note, "file_url", None),
                }
                for note in getattr(submission, "notes", [])
            ],
            "additional_recipients": [
                {
                    "id": recipient.submission_additional_recipients_id,
                    "email": recipient.email,
                }
                for recipient in getattr(submission, "additional_recipients", [])
            ],
        }
        return formatted_data

    def delete_submission(self, submission_id: int):
        try:
            submission = (
                self.session.query(Submission)
                .filter(Submission.submission_id == submission_id)
                .one_or_none()
            )

            if not submission:
                raise None

            self.session.delete(submission)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error in delete_submission: {e}", exc_info=True)
            raise
