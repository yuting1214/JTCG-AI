# app/artifacts/itinerary.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class DayPlan(BaseModel):
    day: int
    activities: List[Dict[str, str]] = []
    meals: List[Dict[str, str]] = []
    transit: List[Dict[str, str]] = []

class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_range: str
    amenities: List[str] = []
    description: str = ""
    
class ItineraryArtifact(BaseModel):
    destination: str
    duration: int
    daily_plans: List[DayPlan] = []
    hotel_recommendations: List[HotelRecommendation] = []
    summary: str = ""
    additional_notes: str = ""
    
    def update_daily_plans(self, new_plans: List[DayPlan]):
        """Update daily plans"""
        self.daily_plans = new_plans
        
    def update_hotels(self, hotels: List[HotelRecommendation]):
        """Update hotel recommendations"""
        self.hotel_recommendations = hotels
        
    def update_summary(self, summary: str):
        """Update itinerary summary"""
        self.summary = summary