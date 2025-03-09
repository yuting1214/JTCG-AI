from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date, datetime

class IntentType(Enum):
    NEW_TRIP = "new_trip"
    UPDATE_ITINERARY = "update_itinerary"
    CLARIFICATION_RESPONSE = "clarification_response"
    UNRELATED = "unrelated"

class IntentionAnalysis(BaseModel):
    intent_type: IntentType
    confidence: float
    action_required: Optional[str] = None
    update_target: Optional[str] = None  # For updates: "activities", "hotels", "dates", etc.

class Location(BaseModel):
    county: str  # For /counties API
    district: Optional[str] = None  # For /districts API
    latitude: Optional[float] = None  # For nearby search
    longitude: Optional[float] = None  # For nearby search

class DayPlan(BaseModel):
    day: int
    location: Location  # Main location for the day
    schedule: List[Dict[str, str]] = []  # Simplified timeline including activities and meals
    # Each dict has: {"time": "09:00", "type": "activity|meal|transit", "description": "...", "location": "台北市信義區"}

    @property
    def activities(self) -> List[Dict[str, str]]:
        """Get all activities for the day"""
        return [item for item in self.schedule if item.get("type") == "activity"]

    @property
    def meals(self) -> List[Dict[str, str]]:
        """Get all meals for the day"""
        return [item for item in self.schedule if item.get("type") == "meal"]

    @property
    def transits(self) -> List[Dict[str, str]]:
        """Get all transit events for the day"""
        return [item for item in self.schedule if item.get("type") == "transit"]
    
# class DayPlan(BaseModel):
#     day: int
#     date: date  # Actual date for hotel booking
#     location: Location  # Primary location for this day
#     activity_times: List[str] = []
#     activity_descriptions: List[str] = []
#     activity_locations: List[Location] = []  # To find hotels near activities
#     meal_times: List[str] = []
#     meal_descriptions: List[str] = []
#     meal_locations: List[Location] = []  # To find hotels near restaurants
#     transit_from: List[str] = []
#     transit_to: List[str] = []
#     transit_mode: List[str] = []

# class HotelPreferences(BaseModel):
#     hotel_type_ids: List[int] = []  # From /hotel_group/types
#     required_facilities: List[int] = []  # From /hotel/facilities
#     room_facilities: List[int] = []  # From /hotel/room_type/facilities
#     preferred_bed_types: List[int] = []  # From /hotel/room_type/bed_types
#     min_price: Optional[float] = None
#     max_price: Optional[float] = None
#     guest_count: int
#     room_count: int

# Pydantic models for API requests
class VacancySearchParams(BaseModel):
    check_in_date: datetime = Field(
        description="Check-in date for the hotel stay"
    )
    check_out_date: datetime = Field(
        description="Check-out date for the hotel stay"
    )
    num_rooms: int = Field(
        description="Number of rooms required",
        ge=1
    )
    num_guests: int = Field(
        description="Total number of guests",
        ge=1
    )

class HotelSearchParams(BaseModel):
    keyword: str = Field(
        description="Hotel name or keyword to search for"
    )

class HotelPlanParams(BaseModel):
    hotel_id: str = Field(
        description="Unique identifier of the hotel"
    )

class HotelRoom(BaseModel):
    room_type: str
    bed_types: List[str]
    facilities: List[str]
    price: float
    available: bool

class HotelRecommendation(BaseModel):
    hotel_id: str
    name: str
    location: Location
    rating: Optional[float]
    rooms: List[HotelRoom]
    nearby_attractions: List[str]

class TravelItinerary(BaseModel):
    daily_plans: List[DayPlan]