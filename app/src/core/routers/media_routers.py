from typing import List, Any

from fastapi import APIRouter, Depends, UploadFile, File, Body
from fastapi.responses import JSONResponse

from app.src.core.schemas.responses.upload_response import UploadMediaResponseModel
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.core.services.upload_service import UploadMediaService


media_router = APIRouter(tags=["Callensights - Media"])

@media_router.post(
    "/upload",
    summary="Upload media file to analyze insights of the media",
    response_model=List[UploadMediaResponseModel] | Any,
    response_model_by_alias=False
)
async def upload_media(
        files: List[UploadFile] = File(...),
        inputs: UploadMediaInputsModel = Body(...),
        upload_service: UploadMediaService = Depends()
):
    response = []
    for file in files:
        response.append(
            upload_service.register_media(file, inputs)
        )

    return JSONResponse(content=response)



