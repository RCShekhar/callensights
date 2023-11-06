from typing import List, Any

from fastapi import APIRouter, Depends, UploadFile, File, Body
from fastapi.responses import JSONResponse

from app.src.core.schemas.requests import GetUploadsRequestModel
from app.src.core.schemas.responses import GetUploadsResponseModel
from app.src.core.services import GetUPloadsService

media_router = APIRouter(tags=["Callensights - Media"])


@media_router.post(
    "/get-uploads",
    summary="Upload media file to analyze insights of the media",
    response_model=GetUploadsResponseModel,
    response_model_by_alias=False
)
async def get_uploads(
        inputs: GetUploadsRequestModel,
        upload_service: GetUploadsRequestModel = Depends()
):


    return JSONResponse(content="")
