from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.src.common.enum.background_enums import BackgroundStageEnum
from app.src.common.security.authorization import DecodedPayload, JWTBearer
from app.src.core.schemas.requests.background_requests import BackgroundTaskRequestModel
from app.src.core.schemas.responses.background_response import BackgroundTaskResponseModel
from app.src.core.services.background_service import BackgroundService

background_router = APIRouter(tags=["Background Tasks"])

@background_router.post(
    "/background-task",
    summary="Request for transcription background task",
    response_model=BackgroundTaskResponseModel,
    response_model_by_alias=False
)
async def background_task(
        request: BackgroundTaskRequestModel,
        bg_tasks: BackgroundTasks,
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        service: BackgroundService = Depends()
) -> JSONResponse:
    user_id = decoded_payload.get('user_id')
    response = service.run_background_task(request, bg_tasks)
    return JSONResponse(content=response.model_dump())

