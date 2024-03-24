from fastapi import APIRouter, Depends
from starlette import status

from app.src.common.security.authorization import JWTBearer, DecodedPayload
from app.src.core.schemas.requests.job_request import CreateJobRequest
from app.src.core.schemas.responses.job_response import (
    CreateJobResponse,
    GetJobFieldValuesResponse,
)
from app.src.core.services.job_service import JobService

job_router = APIRouter(tags=["Jobs"])


@job_router.put(
    "",
    summary="Create Job",
    response_model=CreateJobResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    job_input: CreateJobRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    job_service: JobService = Depends(),
) -> CreateJobResponse:
    user_id = decoded_payload.get("user_id")
    return job_service.create_job(user_id, job_input)


@job_router.get(
    "/create",
    summary="Get Job Field Values",
    response_model=GetJobFieldValuesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_field_values(
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    job_service: JobService = Depends(),
) -> GetJobFieldValuesResponse:
    user_id = decoded_payload.get("user_id")
    return job_service.get_field_values(user_id)


@job_router.get(
    "/{job_id}",
    summary="Get Job",
    status_code=status.HTTP_200_OK,
)
async def get_job(
    job_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    job_service: JobService = Depends(),
):
    user_id = decoded_payload.get("user_id")
    return job_service.get_job(user_id, job_id)


@job_router.delete(
    "/{job_id}",
    summary="Get Job Users",
    status_code=status.HTTP_200_OK,
)
async def delete_jobs(
    job_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    job_service: JobService = Depends(),
) -> None:
    user_id = decoded_payload.get("user_id")
    return job_service.delete_job(user_id, job_id)


@job_router.patch(
    "/{job_id}",
    summary="Update Job",
    response_model=CreateJobResponse,
    status_code=status.HTTP_200_OK,
)
async def update_job(
    job_id: int,
    job_update: CreateJobRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    job_service: JobService = Depends(),
) -> CreateJobResponse:
    user_id = decoded_payload.get("user_id")
    return job_service.update_job(user_id, job_id, job_update)
