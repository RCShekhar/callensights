from datetime import datetime
from typing import Any

import jwt
import uvicorn
from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from app.src.common.constants.global_constants import (
    ALLOWED_ORIGINS,
    ALLOWED_METHODS,
    ALLOWED_HEADERS,
    UNAUTHENTICATED_PATHS,
)

from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.exceptions.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.src.common.security.authorization import JWTDecoder
from app.src.core.routers.media_routers import media_router
from app.src.core.routers.users_routers import user_router
from app.src.core.routers.lead_routers import lead_router
from fastapi.middleware.gzip import GZipMiddleware

application = FastAPI(
    docs_url="/callensights/docs",
    openapi_url="/callensights/openapi",
    title="Callensights",
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)
application.add_middleware(GZipMiddleware, minimum_size=1000)

application.add_exception_handler(BaseAppException, app_exception_handler)
application.add_exception_handler(HTTPException, http_exception_handler)
application.add_exception_handler(RequestValidationError, validation_exception_handler)
application.add_exception_handler(Exception, general_exception_handler)

# application.add_exception_handler()

application.include_router(media_router, prefix="/media")
application.include_router(user_router, prefix="/user")
application.include_router(lead_router, prefix="/lead")

jwt_decoder = JWTDecoder()


@application.middleware("http")
async def app_authorization(request: Request, call_next) -> JSONResponse | Any:
    request_path = request.get("path")
    if request_path in UNAUTHENTICATED_PATHS:
        return await call_next(request)
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                "message": "Bad Request: The Authorization header is not present in your request. Please ensure you include it with the correct 'Bearer' token."
            },
        )
    try:
        decoded_payload = jwt_decoder.decode_jwt(authorization_header)
        request.state.user = decoded_payload
        response = await call_next(request)
        return response
    except jwt.InvalidSignatureError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={
                "message": "Unauthorized: The provided token is invalid. Please ensure you are using the correct token."
            },
        )
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={
                "message": "Unauthorized: The provided token has expired. Please refresh your token."
            },
        )
    except jwt.InvalidTokenError as e:
        print(e)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={
                "message": "Unauthorized: You must be authenticated to perform this request. The provided token is invalid or malformed."
            },
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={
                "message": "An unexpected error occurred. Please try again later, and if the problem persists, contact support."
            },
        )


@application.get("/", tags=["Home"])
async def home():
    return {
        "time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
    }


@application.on_event("startup")
def startup() -> None:
    pass


@application.on_event("shutdown")
def shutdown() -> None:
    pass


if __name__ == "__main__":
    uvicorn.run(application, host="0.0.0.0", port=8081)
