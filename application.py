from datetime import datetime

import jwt
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import Response
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
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


from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            else:
                try:
                    decoded_payload = jwt_decoder.decode_jwt(credentials.credentials)
                except jwt.InvalidSignatureError:
                    raise HTTPException(
                        status_code=403,
                        detail="Unauthorized: The provided token is invalid. Please ensure you are using the correct token.",
                    )
                except jwt.ExpiredSignatureError:
                    raise HTTPException(
                        status_code=403,
                        detail="Unauthorized: The provided token has expired. Please refresh your token.",
                    )
                except jwt.InvalidTokenError:
                    raise HTTPException(
                        status_code=403,
                        detail="Unauthorized: You must be authenticated to perform this request. The provided token is invalid or malformed.f",
                    )
                except Exception:
                    raise HTTPException(
                        status_code=403,
                        detail="An unexpected error occurred. Please try again later, and if the problem persists, contact support.",
                    )

            return decoded_payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


@application.get("/", dependencies=[Depends(JWTBearer())], tags=["Home"])
async def home():
    return {
        "time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
    }


if __name__ == "__main__":
    uvicorn.run(application, host="0.0.0.0", port=8081)
