from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from app.src.common.security.authorization import JWTBearer, DecodedPayload
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
        upload_service: MediaService = Depends(),
        decoaded_payload: DecodedPayload = Depends(JWTBearer())
) -> JSONResponse:
    input_dict = inputs.model_dump()
    input_dict['user_id'] = decoaded_payload.get('user_id')
    response = upload_service.register_media(input_dict)

    return JSONResponse(content=[model.model_dump() for model in response])


@media_router.get(
    "/get-uploads",
    summary="Get list of media uploaded by a specific user",
    response_model=List[GetUploadsResponseModel],
    response_model_by_alias=False
)
async def get_uploads(
        # user_id: str,
        service: MediaService = Depends(),
        decoaded_payload: DecodedPayload = Depends(JWTBearer())
) -> JSONResponse:
    user_id = decoaded_payload.get('user_id')
    response = service.get_uploads(user_id)
    return JSONResponse(content=[model.model_dump() for model in response])


@media_router.get(
    "/get-media",
    summary="Stream media bytes",
    # response_model=StreamingResponse,
    response_model_by_alias=False
)
async def get_media(
        media_code: str,
        media_service: MediaService = Depends(),
        decoaded_payload: DecodedPayload = Depends(JWTBearer())
) -> StreamingResponse:
    user_id = decoaded_payload.get('user_id')
    return media_service.get_media_stream(media_code, user_id)


@media_router.get(
    "/get-feedback",
    summary="Provides feedback of an uploaded media file.",
    response_model_by_alias=False
)
async def get_feedback(
        media_code: str,
        media_service: MediaService = Depends(),
        decoaded_payload: DecodedPayload = Depends(JWTBearer())
) -> JSONResponse:
    user_id = decoaded_payload.get('user_id')
    return media_service.get_feedback(media_code, user_id)


@media_router.get(
    "/get-transcript",
    summary="Provides transcription of an uploaded Media",
    response_model_by_alias=False
)
async def get_transcript(
        media_code: str,
        media_service: MediaService = Depends(),
        decoaded_payload: DecodedPayload = Depends(JWTBearer())
) -> JSONResponse:
    user_id = decoaded_payload.get('user_id')
    return media_service.get_transcription(media_code, user_id)
