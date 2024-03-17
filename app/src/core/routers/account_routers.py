from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.src.common.security.authorization import JWTBearer, DecodedPayload
from app.src.core.schemas.requests.account_request import CreateAccountRequestModel
from app.src.core.schemas.responses.account_response import CreateAccountResponseModel
from app.src.core.services.account_service import AccountService

account_router = APIRouter(tags=["Accounts"])


@account_router.post(
    "/add-account",
    summary="Create account or onboard a client",
    response_model=CreateAccountResponseModel,
    response_model_by_alias=False
)
async def add_account(
        account_input: CreateAccountRequestModel,
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        account_service: AccountService = Depends()
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = account_service.add_account(user_id, account_input)
    return JSONResponse(content=response.model_dump())