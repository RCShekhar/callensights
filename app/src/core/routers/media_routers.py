from typing import List, Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.src.core.schemas.responses.upload_response import MediaResponse
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.core.services.media_service import MediaService

from app.src.core.schemas.requests import GetUploadsRequestModel
from app.src.core.schemas.responses import GetUploadsResponseModel

media_router = APIRouter(tags=["Media"])


@media_router.post(
    "/upload",
    summary="Upload media file to analyze insights of the media",
    response_model=List[MediaResponse],
    response_model_by_alias=False
)
async def upload_media(
        inputs: UploadMediaInputsModel,
        upload_service: MediaService = Depends()
):

    response = upload_service.register_media(inputs)

    return JSONResponse(content=[model.model_dump() for model in response])


@media_router.get(
    "/get-uploads",
    summary="",
    response_model=List[GetUploadsResponseModel],
    response_model_by_alias=False
)
async def get_uploads(
        get_uploads_inputs: GetUploadsRequestModel,
        service: MediaService = Depends()
):
    response = service.get_uploads(get_uploads_inputs)
    return JSONResponse(content=[model.model_dump() for model in response])
