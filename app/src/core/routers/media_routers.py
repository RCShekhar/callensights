from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from app.src.core.schemas.responses.upload_response import MediaResponse
from app.src.core.schemas.requests.upload_request import UploadMediaInputsModel
from app.src.core.services.media_service import MediaService
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
    summary="Get list of media uploaded by a specific user",
    response_model=List[GetUploadsResponseModel],
    response_model_by_alias=False
)
async def get_uploads(
        user_id: str,
        service: MediaService = Depends()
):
    response = service.get_uploads(user_id)
    return JSONResponse(content={'records': [model.model_dump() for model in response]})

@media_router.get(
    "/get-all-uploads",
    summary="Get list of all media uploaded by self and team",
    response_model= List[GetUploadsResponseModel],
    response_model_by_alias=False
)
async def get_all_uploads(
        user_id:str,
        service: MediaService = Depends()
):
    response = service.get_all_uploads(user_id)
    return JSONResponse(content={'records': [model.model_dump() for model in response]})

@media_router.get(
    "/get-media",
    summary="Stream media bytes",
    # response_model=StreamingResponse,
    response_model_by_alias=False
)
async def get_media(
        media_code: str,
        media_service: MediaService = Depends()
) -> StreamingResponse:
    return media_service.get_media_stream(media_code)


@media_router.get(
    "/get-feedback",
    summary="Provides feedback of an uploaded media file.",
    response_model_by_alias=False
)
async def get_feedback(
        media_code: str,
        media_service: MediaService = Depends()
):
    return media_service.get_feedback(media_code)


@media_router.get(
    "/get-transcript",
    summary="Provides transcription of an uploaded Media",
    response_model_by_alias=False
)
async def get_transcript(
        media_code: str,
        media_service: MediaService = Depends()
):
    return media_service.get_transcription(media_code)

