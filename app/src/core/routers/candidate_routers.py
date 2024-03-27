from fastapi import APIRouter, Depends
from starlette import status

from app.src.common.security.authorization import JWTBearer, DecodedPayload
from app.src.core.schemas.requests.candidate_request import (
    CreateCandidateRequest,
    UpdateCandidateRequest,
    UpdateCandidateResumeModel,
)
from app.src.core.schemas.responses.candidate_response import (
    CandidateFormattedResponseModel,
    CreateCandidateResponse,
    GetCandidateFieldValuesResponse,
)
from app.src.core.services.candidate_service import CandidateService

candidate_router = APIRouter(tags=["Candidates"])


@candidate_router.put(
    "",
    summary="Create Candidate",
    response_model=CreateCandidateResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_candidate(
    candidate_input: CreateCandidateRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    candidate_service: CandidateService = Depends(),
) -> CreateCandidateResponse:
    user_id = decoded_payload.get("user_id")
    return candidate_service.add_candidate(user_id, candidate_input)


@candidate_router.get(
    "/{candidate_id}",
    summary="Get Candidate Information",
    response_model=CandidateFormattedResponseModel,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
async def get_candidate(
    candidate_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    candidate_service: CandidateService = Depends(),
) -> CandidateFormattedResponseModel:
    user_id = decoded_payload.get("user_id")
    return candidate_service.get_candidate(user_id, candidate_id)


@candidate_router.get(
    "/{candidate_id}/update",
    summary="Get data for candidate updation",
    response_model=UpdateCandidateRequest,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
async def get_candidate_for_update(
    candidate_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    candidate_service: CandidateService = Depends(),
) -> UpdateCandidateRequest:
    user_id = decoded_payload.get("user_id")
    return candidate_service.get_candidate(user_id, candidate_id, for_update=True)


@candidate_router.patch(
    "/{candidate_id}",
    summary="Update Candidate Information",
    response_model=None,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
async def update_candidate(
    candidate_id: int,
    candidate_input: UpdateCandidateRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    candidate_service: CandidateService = Depends(),
) -> None:
    user_id = decoded_payload.get("user_id")
    return candidate_service.update_candidate(user_id, candidate_id, candidate_input)


@candidate_router.get(
    "/create",
    summary="Get Candidate Field Values",
    response_model=GetCandidateFieldValuesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_field_values(
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    job_service: CandidateService = Depends(),
) -> GetCandidateFieldValuesResponse:
    user_id = decoded_payload.get("user_id")
    return job_service.get_field_values(user_id)


@candidate_router.delete(
    "/{candidate_id}",
    summary="Delete Candidate",
    status_code=status.HTTP_200_OK,
)
async def delete_candidate(
    candidate_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    candidate_service: CandidateService = Depends(),
) -> None:
    user_id = decoded_payload.get("user_id")
    return candidate_service.delete_candidate(user_id, candidate_id)
