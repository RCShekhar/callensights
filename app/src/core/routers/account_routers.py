from fastapi import APIRouter, Depends
from starlette import status

from app.src.common.security.authorization import JWTBearer, DecodedPayload
from app.src.core.schemas.requests.account_request import (
    CreateAccountRequest,
    UpdateAccountRequest,
)
from app.src.core.schemas.responses.account_response import (
    CreateAccountResponse,
    GetAccountResponse,
    UpdateAccountResponse,
)
from app.src.core.services.account_service import AccountService

account_router = APIRouter(tags=["Accounts"])


@account_router.put(
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
    account_service: AccountService = Depends(),
) -> CreateAccountResponse:
    user_id = decoded_payload.get("user_id")
    return account_service.add_account(user_id, account_input)


@account_router.get(
    "/{account_id}",
    summary="Get Account Information",
    response_model=GetAccountResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
async def get_account(
    account_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    account_service: AccountService = Depends(),
) -> GetAccountResponse:
    user_id = decoded_payload.get("user_id")
    return account_service.get_account(user_id, account_id)


@account_router.patch(
    "/{account_id}",
    summary="Get Account Information",
    response_model=UpdateAccountResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
async def get_account(
    account_id: int,
    account_input: UpdateAccountRequest,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    account_service: AccountService = Depends(),
) -> UpdateAccountResponse:
    user_id = decoded_payload.get("user_id")
    return account_service.update_account(user_id, account_id, account_input)


@account_router.delete(
    "/{account_id}",
    summary="Delete Account",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_account(
    account_id: int,
    decoded_payload: DecodedPayload = Depends(JWTBearer()),
    account_service: AccountService = Depends(),
) -> None:
    user_id = decoded_payload.get("user_id")
    account_service.delete_account(user_id, account_id)
    return None
