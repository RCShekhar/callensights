from typing import List, Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.src.core.schemas.responses.upload_response import UploadMediaResponseModel
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.core.services.upload_service import UploadMediaService

from app.src.core.schemas.requests import GetUploadsRequestModel
from app.src.core.schemas.responses import GetUploadsResponseModel
from app.src.core.services import GetUPloadsService

media_router = APIRouter(tags=["Media"])


@media_router.post(
    "/upload",
    summary="Upload media file to analyze insights of the media",
    response_model=UploadMediaResponseModel,
    response_model_by_alias=False
)
async def upload_media(
        inputs: UploadMediaInputsModel,
        upload_service: UploadMediaService = Depends()
):
    data = inputs.model_dump()
    response = []
    for file in data.get('files', []):
        response.append(
            upload_service.register_media(file, inputs)
        )

    upload_response = UploadMediaResponseModel.model_validate(*response)

    return JSONResponse(content=upload_response.model_dump())


@media_router.get(
    "/get-uploads",
    summary="",
    response_model=GetUploadsResponseModel,
    response_model_by_alias=False
)
async def get_uploads(
        inputs: GetUploadsRequestModel,
        service: GetUPloadsService = Depends()
):
    pass