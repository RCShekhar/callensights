from typing import Any, Dict, List

from fastapi import Depends

from app.src.common.config.app_settings import Settings, get_app_settings
from app.src.core.repositories.dashboard_repository import DashboardRepository
from app.src.core.schemas.responses.dashboard_responses import (
    OverallMetricsModel,
    MonthlyUploadsModel,
    RecentCallsModel,
)
from app.src.core.services.base_service import BaseService


class DashboardService(BaseService):

    def __init__(
        self,
        repository: DashboardRepository = Depends(),
        settings: Settings = Depends(get_app_settings),
    ):
        super().__init__("Dashboard Service")
        self.repository = repository
        self.settings = settings

    def get_overall_metrics(self, user_id: str) -> List[Dict[str, Any]]:
        self.repository.assume_user_exists(user_id)
        uploads = self.repository.get_uploads(user_id)
        upload_count = len(uploads)
        total_media_length = sum([media.get("media_length", 0.0) for media in uploads])
        response = {
            "TOTAL_CALLS_UPLOADED": upload_count,
            "AVERAGE_CALL_DURATION": (
                total_media_length
                if total_media_length == 0.0
                else total_media_length / upload_count
            ),
            "OVERALL_SCORE": 0.0,
        }

        individual_scores = {}
        media_codes = [media["media_code"] for media in uploads]
        for media_code in media_codes:
            metrics = self.repository.get_media_metrics(media_code)
            for metric in metrics:
                key = metric.get("metric_name")
                rating = float(metric.get("rating"))
                if key in response:
                    individual_scores[key] += rating
                    individual_scores[key] /= 2
                else:
                    individual_scores[key] = rating

        response["OVERALL_SCORE"] = sum(list(individual_scores.values()))
        response.update(individual_scores)
        result = [
            {"metric_name": key, "rating": value} for key, value in response.items()
        ]

        return [
            OverallMetricsModel.model_validate(data).model_dump() for data in result
        ]

    def monthly_uploads(self, user_id: str) -> List[Dict[str, int]]:
        self.repository.assume_user_exists(user_id)
        uploads = self.repository.get_monthly_uploads(user_id)

        return [
            MonthlyUploadsModel.model_validate(
                {"month": month, "calls_uploaded": calls_uploaded}
            ).model_dump()
            for month, calls_uploaded in uploads.items()
        ]

    def get_recent_calls(self, user_id: str) -> List[Dict[str, Any]]:
        self.repository.assume_user_exists(user_id)
        recent_calls = self.repository.get_recent_calls(user_id)
        calls = []
        for call in recent_calls:
            assigned_to = {
                "user_id": call.pop("user_id"),
                "user_name": call.pop("user_name"),
            }
            call["assigned_to"] = assigned_to
            calls.append(call)

        return [RecentCallsModel.model_validate(call).model_dump() for call in calls]
