from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.src.common.security.authorization import DecodedPayload, JWTBearer
from app.src.core.services.user_services import UserService
from app.src.core.schemas.responses.user_workspace_response import UserWorkspaceResponse

user_router = APIRouter(tags=["Users"])


@user_router.get(
    "/workspace",
    summary="User workspace data",
    response_model=UserWorkspaceResponse,
    response_model_by_alias=False
)
async def user_workspace(
        service: UserService = Depends(),
        decoaded_payload: DecodedPayload = Depends(JWTBearer())
) -> UserWorkspaceResponse:
    user_id = decoaded_payload.get('user_id')
    response = service.get_user_workspace(user_id)
    return response
