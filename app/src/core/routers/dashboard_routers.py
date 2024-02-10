from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.src.common.security.authorization import DecodedPayload, JWTBearer
from app.src.core.schemas.responses.dashboard_responses import (
    OverallMetricsModel,
    MonthlyUploadsModel,
    RecentCallsModel)
from app.src.core.services.dashboard_service import DashboardService

dashboard_router = APIRouter(tags=["Dashboard"])


@dashboard_router.get(
    "/overall-metrics",
    summary="Average metric score",
    response_model=List[OverallMetricsModel],
    response_model_by_alias=False
)
async def overall_metrics(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        dashboard_service: DashboardService = Depends()
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = dashboard_service.get_overall_metrics(user_id)
    return JSONResponse(content=response)


@dashboard_router.get(
    "/monthly-uploads",
    summary="Number of uploads made for each month",
    response_model=List[MonthlyUploadsModel],
    response_model_by_alias=False
)
async def monthly_uploads(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        dashboard_service: DashboardService = Depends()
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = dashboard_service.monthly_uploads(user_id)
    return JSONResponse(content=response)


@dashboard_router.get(
    "/recent-calls",
    summary="Get 5 recent calls",
    response_model=List[RecentCallsModel],
    response_model_by_alias=False
)
async def recent_calls(
        decoded_payload: DecodedPayload = Depends(JWTBearer()),
        dashboard_service: DashboardService = Depends()
) -> JSONResponse:
    user_id = decoded_payload.get("user_id")
    response = dashboard_service.get_recent_calls(user_id)
    return JSONResponse(content=response)
