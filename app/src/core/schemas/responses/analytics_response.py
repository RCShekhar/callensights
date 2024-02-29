from typing import List
from pydantic import BaseModel


class Average(BaseModel):
    date: str
    average_rating: float


class CsatScoreModel(BaseModel):
    averages: List[Average]


class Lead(BaseModel):
    lead_id: int
    lead_name: str
    lead_at: str


class Calls(BaseModel):
    media_code: str
    lead: Lead
    rating: float


class OptimalFrailCallsModel(BaseModel):
    optimal_calls: List[Calls]
    frail_calls: List[Calls]


class CallRatingMetricsModel(BaseModel):
    metric: str
    average_rating: float
