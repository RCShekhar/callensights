from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware

from app.src.common.constants.global_constants import (
    ALLOWED_ORIGINS,
    ALLOWED_METHODS,
    ALLOWED_HEADERS,
)

from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.exceptions.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.src.core.routers.media_routers import media_router
from app.src.core.routers.users_routers import user_router
from app.src.core.routers.lead_routers import lead_router
from fastapi.middleware.gzip import GZipMiddleware

from app.src.common.security.authorization import JWTBearer

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


@application.get("/", dependencies=[Depends(JWTBearer())], tags=["Home"])
async def home(bearer: JWTBearer = Depends()):
    return {
        "time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
    }


if __name__ == "__main__":
    uvicorn.run(application, host="0.0.0.0", port=8000)
