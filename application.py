from datetime import datetime
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError

from app.src.common.exceptions.application_exception import BaseAppException
from app.src.common.exceptions.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler
)
from app.src.core.routers.media_routers import media_router
application = FastAPI(
    docs_url="/callensights/docs",
    openapi_url="/callensights/openapi"
)

application.add_exception_handler(BaseAppException, app_exception_handler)
application.add_exception_handler(HTTPException, http_exception_handler)
application.add_exception_handler(RequestValidationError, validation_exception_handler)
application.add_exception_handler(Exception, general_exception_handler)


# application.add_exception_handler()

application.include_router(media_router, prefix="/media")

@application.get("/", tags=["Callensights"])
async def home():
    return {"time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}


@application.on_event("startup")
def startup() -> None:
    pass


@application.on_event("shutdown")
def shutdown() -> None:
    pass
