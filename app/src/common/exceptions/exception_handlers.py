import traceback
from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.src.common.exceptions.application_exception import BaseAppException


def log_exception(exc: BaseException, request: Request) -> None:
    pass


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    log_exception(exc, request)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_description": exc.description,
            "error_message": traceback.format_exc()
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    log_exception(exc, request)

    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={'message': "FAILED", 'details':  exc.errors()}
    )


async def general_exception_handler(request: Request, exc: BaseException) -> JSONResponse:
    log_exception(exc, request)

    return JSONResponse(
        status_code=500,
        content={"message": "FAILED", "details": "An Unknown error occurred."}
    )
