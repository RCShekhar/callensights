from typing import List
from pydantic import BaseModel


class Average(BaseModel):
    date: str
    average_rating: float


class CsatScoreModel(BaseModel):
    averages: List[Average]
    overall_average: float


class Calls(BaseModel):
    media_code: str
    rating: float


class OptimalFrailCallsModel(BaseModel):
    optimal_calls: List[Calls]
    frail_calls: List[Calls]

class CallRatingMetricsModel(BaseModel):
    metric: str
    average_rating: float