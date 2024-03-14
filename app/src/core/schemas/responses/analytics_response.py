from typing import List, Dict, Any, Union
from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    username: str


class Lead(BaseModel):
    lead_id: int
    lead_name: str
    lead_at: str


class Average(BaseModel):
    date: str
    average_rating: float


class CsatScoreModel(BaseModel):
    averages: List[Average]


class Calls(BaseModel):
    media_code: str
    lead: Lead
    rating: float


class OptimalFrailCallsModel(BaseModel):
    frail_calls: List[Calls]
    optimal_calls: List[Calls]


class CallRatingMetricsModel(BaseModel):
    metrics: List[Dict[str, Any]]
    user: User
    lead: Lead
    media_code: str


class CustomerSatisfactionScoreModel(BaseModel):
    timestamp: str
    media_code: str
    user: User
    lead: Lead
    average_rating: float


class CustomerSatisfactionScoreListModel(BaseModel):
    averages: List[CustomerSatisfactionScoreModel]


class AverageCallDurationModel(BaseModel):
    duration: Union[float, int]
    media_code: str
    timestamp: str
    lead: Lead
    user: User
