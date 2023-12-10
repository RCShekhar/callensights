from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.src.core.services.user_services import UserService
from app.src.core.schemas.requests.create_user_request import CreateUserRequest
from app.src.core.schemas.responses.create_user_response import CreateUserResponse
from app.src.core.schemas.requests.create_user_group_request import CreateUserGroupRequest
from app.src.core.schemas.responses.create_user_group_response import CreateUserGroupResponse
from app.src.core.schemas.requests.update_user_request import UpdateUserRequest
from app.src.core.schemas.responses.user_workspace_response import UserWorkspaceResponse

user_router = APIRouter(tags=["Users"])


@user_router.post(
    "/create-user",
    summary="Create a Callensights user",
    response_model=CreateUserResponse,
    response_model_by_alias=False
)
def create_user(
        inputs: CreateUserRequest,
        service: UserService = Depends()
) -> JSONResponse:
    response = service.create_user(inputs)
    return JSONResponse(content=response)


@user_router.post(
    "/create-user-group",
    summary="Create a new user_group",
    response_model=CreateUserGroupResponse,
    response_model_by_alias=False
)
def create_user_group(
        inputs: CreateUserGroupRequest,
        service: UserService = Depends()
) -> JSONResponse:
    response = service.create_user_group(inputs)
    return JSONResponse(content=response)


@user_router.patch(
    "/update-user",
    summary="Update user details",
    response_model_by_alias=False
)
def update_user(
        user_id: str,
        user_data: UpdateUserRequest,
        service: UserService = Depends()
) -> JSONResponse:
    response = service.update_user(user_id, user_data)
    return JSONResponse(content={"status": response})


@user_router.delete(
    "/user-delete",
    summary="Delete an existing user",
    response_model_by_alias=False
)
def delete_user(
        user_id: str,
        service: UserService = Depends()
) -> JSONResponse:
    response = service.delete_user(user_id)
    return JSONResponse(content={"status": response})


@user_router.get(
    "/workspace",
    summary="User workspace data",
    response_model=UserWorkspaceResponse,
    response_model_by_alias=False
)
def user_workspace(
        user_id: str,
        service: UserService = Depends()
) -> UserWorkspaceResponse:
    response = service.get_user_workspace(user_id)
    return response
