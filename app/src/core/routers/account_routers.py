from fastapi import APIRouter, Depends
from starlette import status

from app.src.common.security.authorization import JWTBearer, DecodedPayload
from app.src.core.schemas.requests.account_request import CreateAccountRequest
from app.src.core.schemas.responses.account_response import CreateAccountResponse
from app.src.core.services.account_service import AccountService

account_router = APIRouter(tags=["Accounts"])


@account_router.post(
    "",
    summary="Create account or Onboard a Client",
    response_model=CreateAccountResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Account with the given name already exists."
        },
    },
)
async def create_account(
        account_input: CreateAccountRequest,
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        account_service: AccountService = Depends()
) -> CreateAccountResponse:
    user_id = decoded_payload.get("user_id")
    return account_service.add_account(user_id, account_input)
