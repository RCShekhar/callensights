from typing import Any, Dict, List

from fastapi import Depends

from app.src.common.config.app_settings import Settings, get_app_settings
from app.src.core.repositories.dashboard_repository import DashboardRepository
from app.src.core.repositories.media_repository import MediaRepository
from app.src.core.schemas.responses.dashboard_responses import (
    OverallMetricsModel,
    MonthlyUploadsModel,
    RecentCallsModel,
)
from app.src.core.services.analytics_service import AnalyticsService
from app.src.core.services.base_service import BaseService


class DashboardService(BaseService):

    def __init__(
            self,
            dashboard_repository: DashboardRepository = Depends(),
            media_repository: MediaRepository = Depends(),
            analytics_service: AnalyticsService = Depends(),
            settings: Settings = Depends(get_app_settings),
    ):
        super().__init__("Dashboard Service")
        self.dashboard_repository = dashboard_repository
        self.media_repository = media_repository
        self.analytics_service = analytics_service
        self.settings = settings

    def get_overall_metrics(self, user_id: str) -> List[Dict[str, Any]]:
        self.dashboard_repository.assume_user_exists(user_id)
        uploads = self.media_repository.get_uploads(user_id)
        upload_count = len(uploads)
        total_media_length = sum([media[3] or 0.0 for media in uploads])
        overall_score = self.analytics_service.get_overall_score(user_id)
        response = {
            "TOTAL_CALLS_UPLOADED": upload_count,
            "AVERAGE_CALL_DURATION": round(
                (
                    total_media_length
                    if total_media_length == 0.0
                    else total_media_length / upload_count
                ),
                2,
            ),
            "OVERALL_SCORE": overall_score,
        }

        result = [
            {"metric_name": key, "rating": value} for key, value in response.items()
        ]

        return [
            OverallMetricsModel.model_validate(data).model_dump() for data in result
        ]

    def monthly_uploads(self, user_id: str) -> List[Dict[str, int]]:
        self.dashboard_repository.assume_user_exists(user_id)
        uploads = self.dashboard_repository.get_monthly_uploads(user_id)

        return [
            MonthlyUploadsModel.model_validate(
                {"month": month, "calls_uploaded": calls_uploaded}
            ).model_dump()
            for month, calls_uploaded in uploads.items()
        ]

    def get_recent_calls(self, user_id: str) -> List[Dict[str, Any]]:
        self.dashboard_repository.assume_user_exists(user_id)
        recent_calls = self.dashboard_repository.get_recent_calls(user_id)
        calls = []
        for call in recent_calls:
            assigned_to = {
                "user_id": call.pop("user_id"),
                "user_name": call.pop("user_name"),
            }
            call["assigned_to"] = assigned_to
            calls.append(call)

        return [RecentCallsModel.model_validate(call).model_dump() for call in calls]
