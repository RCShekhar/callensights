from datetime import datetime

import jwt
import uvicorn
from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import Response
from starlette.middleware.cors import CORSMiddleware

from app.src.common.constants.global_constants import ALLOWED_ORIGINS, ALLOWED_METHODS, ALLOWED_HEADERS
from app.src.common.enum.custom_error_code import CustomErrorCode
from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.exceptions.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler
)
from app.src.common.security.authorization import JWTDecoder
from app.src.core.routers.media_routers import media_router
from app.src.core.routers.users_routers import user_router
from app.src.core.routers.lead_routers import lead_router

application = FastAPI(
    docs_url="/callensights/docs",
    openapi_url="/callensights/openapi",
    title="Callensights"
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

application.add_exception_handler(BaseAppException, app_exception_handler)
application.add_exception_handler(HTTPException, http_exception_handler)
application.add_exception_handler(RequestValidationError, validation_exception_handler)
application.add_exception_handler(Exception, general_exception_handler)

# application.add_exception_handler()

application.include_router(media_router, prefix="/media")
application.include_router(user_router, prefix="/user")
application.include_router(lead_router, prefix="/lead")


@application.middleware('http')
async def app_authorization(request: Request, call_next) -> Response:
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        raise BaseAppException(
            status_code=400,
            description="Invalid Authorization token",
            data = {'message': "Authorization header is missing"},
            custom_error_code=CustomErrorCode.AUTHORIZATION_ERROR
        )
    jwt_decoder = JWTDecoder()
    try:
        decoded_payload = jwt_decoder.decode_jwt(authorization_header)
        response = await call_next(decoded_payload)
        return response
    except jwt.ExpiredSignatureError as e:
        raise BaseAppException(
            status_code=401,
            data={'message': str(e)},
            description="JWT Error: Token Expired",
            custom_error_code=CustomErrorCode.AUTHORIZATION_ERROR
        )
    except jwt.InvalidTokenError as e:
        raise BaseAppException(
            status_code=401,
            description="JWT Error: Invalid Token",
            data={'message':str(e)},
            custom_error_code=CustomErrorCode.AUTHORIZATION_ERROR
        )
    except Exception as e:
        raise BaseAppException(
            status_code=401,
            description="Unknown JWT exception",
            data={'message': str(e)},
            custom_error_code=CustomErrorCode.UNKNOWN_ERROR
        )



@application.get("/", tags=["Home"])
async def home():
    return {"time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}


@application.on_event("startup")
def startup() -> None:
    pass


@application.on_event("shutdown")
def shutdown() -> None:
    pass


if __name__ == "__main__":
    uvicorn.run(application, host="0.0.0.0", port=8081)
