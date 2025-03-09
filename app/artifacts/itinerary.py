# app/artifacts/itinerary.py
from pydantic import BaseModel
from typing import List, Optional
from app.workflow.models import (
    DayPlan,
    TravelItinerary,
    HotelRecommendation
)

class ItineraryArtifact(BaseModel):
    itinerary: Optional[TravelItinerary] = None
    hotel_recommendations: List[HotelRecommendation] = []

    # Additional information
    summary: str = ""
    additional_notes: str = ""
    
    def update_itinerary(self, new_itinerary: TravelItinerary):
        """Update the entire travel itinerary"""
        self.itinerary = new_itinerary
        
    def update_daily_plans(self, new_plans: List[DayPlan]):
        """Update just the daily plans within the itinerary"""
        if self.itinerary:
            self.itinerary.daily_plans = new_plans
            
    def update_hotels(self, hotels: List[HotelRecommendation]):
        """Update hotel recommendations"""
        self.hotel_recommendations = hotels
        
    def update_summary(self, summary: str):
        """Update itinerary summary"""
        self.summary = summary
        
    def add_note(self, note: str):
        """Add additional note"""
        if self.additional_notes:
            self.additional_notes += f"\n{note}"
        else:
            self.additional_notes = note