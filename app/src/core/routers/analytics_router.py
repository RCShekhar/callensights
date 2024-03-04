import logging
from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.src.common.security.authorization import DecodedPayload, JWTBearer
from app.src.core.schemas.responses.analytics_response import (
    CallRatingMetricsModel,
    CustomerSatisfactionScoreListModel,
    OptimalFrailCallsModel,
)
from app.src.core.services.analytics_service import AnalyticsService

analytics_router = APIRouter(tags=["Analytics"])

logger = logging.getLogger(__name__)


@analytics_router.get(
    "/csat-scores",
    summary="Average metric score",
    response_model=CustomerSatisfactionScoreListModel,
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
async def optimal_and_frail_calls(
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
async def call_rating_metrics(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        analytics_service: AnalyticsService = Depends(),
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = analytics_service.get_call_rating_metrics(user_id)
    return JSONResponse(content=response)


@analytics_router.get(
    "/average-call-duration",
    summary="Call Rating Metrics",
    response_model=List[CallRatingMetricsModel],
    response_model_by_alias=False,
)
async def average_call_duration(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        analytics_service: AnalyticsService = Depends(),
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = analytics_service.average_call_duration(user_id)
    return JSONResponse(content=response)
