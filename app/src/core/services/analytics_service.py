import heapq
import re
from typing import Dict, Any
from fastapi import Depends
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from app.src.common.config.app_settings import Settings, get_app_settings
from app.src.core.repositories.analytics_repository import AnalyticsRepository
from app.src.core.repositories.media_repository import MediaRepository
from app.src.core.schemas.responses.analytics_response import (
    CallRatingMetricsModel,
    OptimalFrailCallsModel,
    CustomerSatisfactionScoreModel,
    CustomerSatisfactionScoreListModel, AverageCallDurationModel,
)
from app.src.core.services.base_service import BaseService
from cachetools import cached, TTLCache

Metric = namedtuple("Metric", ["name", "rating"])

fn_cache = TTLCache(maxsize=100, ttl=1800)
uploads_cache = TTLCache(maxsize=100, ttl=600)


class AnalyticsService(BaseService):
    """
    A service class for handling analytics related operations.
    """

    def __init__(
            self,
            analytics_repository: AnalyticsRepository = Depends(),
            media_repository: MediaRepository = Depends(),
            settings: Settings = Depends(get_app_settings),
    ):
        """
        Initializes the class with repositories and settings.
        """
        super().__init__("Analytics Service")
        self.CACHE_EXPIRATION_DURATION = timedelta(minutes=10)
        self.analytics_repository = analytics_repository
        self.media_repository = media_repository
        self.application_settings = settings
        self.rating_pattern = re.compile(r"(\d+)/\d+|\d+(\.\d+)?")
        self.feedback_cache = None
        self.cache_timestamp = None

    def calculate_average_rating(self, metrics_list):
        """
        Calculates the average rating from a list of metrics.
        """
        ratings = [
            self.parse_rating(metric["rating"])
            for metric in metrics_list
            if self.is_valid_rating(metric["rating"])
        ]
        valid_ratings = list(rating for rating in ratings if rating is not None)
        return sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0

    @property
    def feedbacks(self):
        """
        Returns cached feedbacks. If the cache is expired or not yet set, it fetches the feedbacks from the
        repository and updates the cache.
        """
        if (
                self.feedback_cache is None
                or datetime.now() - self.cache_timestamp > self.CACHE_EXPIRATION_DURATION
        ):
            self.feedback_cache = self.analytics_repository.get_all_feedbacks()
            self.cache_timestamp = datetime.now()
        return self.feedback_cache

    @cached(uploads_cache)
    def get_uploads(self, user_id: str):
        """
        Returns the uploads for a user. The results are cached for 10 minutes.
        """
        return self.media_repository.get_uploads(user_id)

    @cached(fn_cache)
    def get_customer_satisfaction_score(self, user_id: str) -> dict[str, Any]:
        """
        Calculates the Customer Satisfaction (CSAT) score for a user. It fetches the user's uploads and feedbacks,
        calculates the average rating for each feedback, and returns the average ratings per day and the overall
        average rating.
        """
        self.analytics_repository.assume_user_exists(user_id)
        user_uploaded_media = self.get_uploads(user_id)
        user_feedbacks = self.feedbacks

        feedbacks_by_media_code = self.get_feedbacks_by_media_code(user_feedbacks)

        customer_satisfaction_scores: CustomerSatisfactionScoreModel = []
        for upload in user_uploaded_media:
            matching_feedback = feedbacks_by_media_code.get(upload[0])
            if matching_feedback:
                feedback_item = matching_feedback
                metrics = feedback_item["feedback"]["metrics"]
                average_rating = self.calculate_average_rating(metrics)
                if upload[6]:
                    customer_satisfaction_scores.append(
                        {
                            "timestamp": upload[4].strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                            "media_code": upload[0],
                            "user": {"user_id": upload[5], "username": upload[6]},
                            "lead": {
                                "lead_id": upload[7],
                                "lead_name": upload[8],
                                "lead_at": upload[9],
                            },
                            "average_rating": average_rating,
                        }
                    )
        return CustomerSatisfactionScoreListModel.model_validate(
            {"averages": [data for data in customer_satisfaction_scores]}
        ).model_dump()

    @cached(fn_cache)
    def get_overall_score(self, user_id: str) -> float:
        """
        Calculates the Customer Satisfaction (CSAT) score for a user. It fetches the user's uploads and feedbacks,
        calculates the average rating for each feedback, and returns the average ratings per day and the overall
        average rating.
        """
        self.analytics_repository.assume_user_exists(user_id)
        user_uploaded_media = self.get_uploads(user_id)
        user_feedbacks = self.feedbacks

        feedbacks_by_media_code = self.get_feedbacks_by_media_code(user_feedbacks)

        overall_score = []
        for upload in user_uploaded_media:
            matching_feedback = feedbacks_by_media_code.get(upload[0])
            if matching_feedback:
                feedback_item = matching_feedback
                metrics = feedback_item["feedback"]["metrics"]
                average_rating = self.calculate_average_rating(metrics)
                overall_score.append(average_rating)

        if overall_score and len(overall_score) > 0:
            return round(sum(overall_score) / len(overall_score), 2)
        else:
            return 0.0

    @staticmethod
    def process_feedback_records(user_feedbacks):
        """
        Processes feedback records to calculate the average rating per day and the overall average rating.
        """
        date_ratings = defaultdict(lambda: {"sum": 0, "count": 0})
        for feedback in user_feedbacks:
            date = datetime.strptime(
                feedback["timestamp"], "%Y-%m-%dT%H:%M:%S%z"
            ).date()
            date_ratings[date]["sum"] += feedback["average_rating"]
            date_ratings[date]["count"] += 1
        averages = [
            {
                "date": date.isoformat(),
                "average_rating": round(values["sum"] / values["count"], 2),
            }
            for date, values in date_ratings.items()
        ]
        averages.sort(key=lambda x: x["date"])
        return {
            "averages": averages,
        }

    def average_call_duration(self, user_id: str):
        self.media_repository.assume_user_exists(user_id)
        uploads = self.media_repository.get_uploads(user_id)
        total_media = [
            {
                "duration": media[3],
                "media_code": media[0],
                "timestamp": media[4].strftime("%Y-%m-%d"),
                "lead": {
                    "lead_id": media[7],
                    "lead_name": media[8],
                },
                "user": {
                    "user_id": media[5],
                    "username": media[6]
                }
            }
            or 0.0 for media in uploads
            if media[3] is not None
        ]

        return [AverageCallDurationModel.model_validate(
            {
                "duration": media["duration"],
                "media_code": media["media_code"],
                "timestamp": media["timestamp"],
                "lead": media["lead"],
                "user": media["user"]
            }
        ).model_dump() for media in total_media]

    @cached(fn_cache)
    def get_optimal_and_frail_calls(self, user_id: str) -> Dict[str, Any]:
        """
        Finds the top 3 calls with the highest ratings (optimal calls) and the top 3 calls with the lowest ratings (
        frail calls).
        """
        self.analytics_repository.assume_user_exists(user_id)
        user_uploaded_media = self.get_uploads(user_id)
        user_feedbacks = self.feedbacks
        calls_data = []
        feedbacks_by_media_code = self.get_feedbacks_by_media_code(user_feedbacks)
        for upload in user_uploaded_media:
            matching_feedback = feedbacks_by_media_code.get(upload[0])
            if matching_feedback:
                feedback_item = matching_feedback
                metrics = feedback_item["feedback"]["metrics"]
                average_rating = self.calculate_average_rating(metrics)
                calls_data.append(
                    (
                        {
                            "media_code": upload[0],
                            "lead": {
                                "lead_id": upload[7],
                                "lead_name": upload[8],
                                "lead_at": upload[9],
                            },
                            "rating": average_rating,
                        }
                    )
                )

        if len(calls_data) < 3:
            return {"optimal_calls": [], "frail_calls": []}

        optimal_calls = heapq.nlargest(3, calls_data, key=lambda x: x["rating"])
        frail_calls = heapq.nsmallest(3, calls_data, key=lambda x: x["rating"])

        return OptimalFrailCallsModel.model_validate(
            {
                "optimal_calls": optimal_calls,
                "frail_calls": frail_calls,
            }
        ).model_dump()

    @cached(fn_cache)
    def get_call_rating_metrics(self, user_id: str) -> list[dict[str, Any]]:
        """
        Calculates the average rating for each metric across all calls for a given user.
        """
        self.analytics_repository.assume_user_exists(user_id)
        uploaded_media = self.get_uploads(user_id)
        user_feedbacks = self.feedbacks

        feedbacks_by_media_code = self.get_feedbacks_by_media_code(user_feedbacks)

        calls_data = [
            {
                "metrics": feedbacks_by_media_code[upload[0]]["feedback"][
                    "metrics"
                ],
                "user": {
                    "user_id": upload[5],
                    "username": upload[6],
                },
                "lead": {
                    "lead_id": upload[7],
                    "lead_name": upload[8],
                    "lead_at": upload[9],
                },
                "media_code": upload[0],
            }
            for upload in uploaded_media
            if upload[0] in feedbacks_by_media_code
        ]

        metric_sums = defaultdict(float)
        metric_counts = defaultdict(int)

        for call in calls_data:
            for metric in call["metrics"]:
                metric_name = metric["metric_name"]

                if not self.is_valid_rating(metric["rating"]):
                    continue

                rating = self.parse_rating(metric["rating"])
                if rating is None:
                    continue

                metric_sums[metric_name] += rating
                metric_counts[metric_name] += 1

        return [CallRatingMetricsModel.model_validate(
            {
                "metric_name": metric_name,
                "average_rating": round(
                    metric_sums[metric_name] / metric_counts[metric_name], 2
                ),
            }
        ).model_dump() for metric_name in metric_sums]

    @staticmethod
    def is_valid_rating(rating: Any) -> bool:
        """
        Checks if a rating is valid (i.e., it is a string, float, or integer).
        """
        return isinstance(rating, (str, float, int))

    @staticmethod
    def get_feedbacks_by_media_code(user_feedbacks):
        """
        Returns a dictionary mapping media codes to feedbacks.
        """
        return {feedback["media_code"]: feedback for feedback in user_feedbacks}

    def parse_rating(self, rating: str) -> float | None:
        """
        Parses a rating from a string to a float.
        """
        if isinstance(rating, str):
            match = self.rating_pattern.search(rating)
            if match:
                return float(match.group(1) if match.group(1) else match.group(0))
            return None

    @staticmethod
    def construct_customer_satisfaction_score(
            upload: Any, average_rating: float
    ) -> Dict[str, Any]:
        """
        Constructs a CSAT score record from an upload and an average rating.
        """
        return {
            "timestamp": upload[4].strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            "media_code": upload[0],
            "average_rating": average_rating,
        }
