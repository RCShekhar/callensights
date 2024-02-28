from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.src.common.security.authorization import DecodedPayload, JWTBearer
from app.src.core.schemas.responses.analytics_response import (
    CallRatingMetricsModel,
    CsatScoreModel,
    OptimalFrailCallsModel,
)
from app.src.core.services.analytics_service import AnalyticsService

analytics_router = APIRouter(tags=["Analytics"])


@analytics_router.get(
    "/csat-scores",
    summary="Average metric score",
    response_model=List[CsatScoreModel],
    response_model_by_alias=False,
)
async def csat_score(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        analytics_service: AnalyticsService = Depends(),
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = analytics_service.get_customer_satisfaction_score(user_id)
    return JSONResponse(content=response)


@analytics_router.get(
    "/optimal-frail-calls",
    summary="Optimal And Frail Calls",
    response_model=List[OptimalFrailCallsModel],
    response_model_by_alias=False,
)
async def csat_score(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        analytics_service: AnalyticsService = Depends(),
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = analytics_service.get_optimal_and_frail_calls(user_id)
    return JSONResponse(content=response)


@analytics_router.get(
    "/call-rating-metrics",
    summary="Call Rating Metrics",
    response_model=List[CallRatingMetricsModel],
    response_model_by_alias=False,
)
async def csat_score(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        analytics_service: AnalyticsService = Depends(),
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = analytics_service.get_call_rating_metrics(user_id)
    return JSONResponse(content=response)
