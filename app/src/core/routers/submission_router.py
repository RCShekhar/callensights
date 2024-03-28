from fastapi import APIRouter, Depends
from starlette import status

from app.src.common.security.authorization import DecodedPayload, JWTBearer
from app.src.core.schemas.requests.submission_request import (
    CreateSubmissionRequest,
    UpdateSubmissionRequest,
)
from app.src.core.schemas.responses.submission_response import (
    CreateSubmissionResponse,
    GetSubmissionResponse,
    BaseResponse,
)
from app.src.core.services.submission_service import SubmissionService

submission_router = APIRouter(tags=["Submission"])


@submission_router.put(
    "",
    summary="Create Submission",
    response_model=CreateSubmissionResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    submission_input: CreateSubmissionRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    submission_service: SubmissionService = Depends(),
) -> CreateSubmissionResponse:
    user_id = decoded_payload.get("user_id")
    return submission_service.create_submission(user_id, submission_input)


@submission_router.get(
    "/create",
    summary="Get Field Values for Updating Submission",
    response_model=CreateSubmissionRequest,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def get_submissions_for_job(
    submission_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    submission_service: SubmissionService = Depends(),
) -> CreateSubmissionRequest:
    user_id = decoded_payload.get("user_id")
    return submission_service.get_rsubmission(user_id, submission_id, for_update=True)


@submission_router.get(
    "/{submission_id}",
    summary="Get Submission Information",
    response_model=GetSubmissionResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def get_submission(
    submission_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    submission_service: SubmissionService = Depends(),
) -> GetSubmissionResponse:
    user_id = decoded_payload.get("user_id")
    return submission_service.get_submission(user_id, submission_id)


@submission_router.patch(
    "/{submission_id}",
    summary="Update Submission",
    response_model=BaseResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def update_submission(
    submission_id: int,
    submission_input: UpdateSubmissionRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    submission_service: SubmissionService = Depends(),
) -> BaseResponse:
    user_id = decoded_payload.get("user_id")
    return submission_service.update_submission(
        user_id, submission_id, submission_input
    )


@submission_router.delete(
    "/{submission_id}",
    summary="Delete Submission",
    response_model=BaseResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def delete_submission(
    submission_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    submission_service: SubmissionService = Depends(),
) -> BaseResponse:
    user_id = decoded_payload.get("user_id")
    return submission_service.delete_submission(user_id, submission_id)
