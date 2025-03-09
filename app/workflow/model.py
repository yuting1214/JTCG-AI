# app/models/itinerary.py
from pydantic import BaseModel
from typing import List, Optional

class TravelContext(BaseModel):
    destination: str
    duration: int
    group_size: int
    budget: Optional[str]
    preferences: List[str] = []

class DailyPlan(BaseModel):
    day: int
    activities: List[dict]
    meals: List[dict]
    transit: List[dict]

class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_range: str
    amenities: List[str]
    description: str

class ItineraryContent(BaseModel):
    context: TravelContext
    daily_plans: List[DailyPlan] = []
    hotel_recommendations: List[HotelRecommendation] = []
    summary: str = ""