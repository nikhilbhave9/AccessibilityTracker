from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Optional
# What sort of classes will we need? 
# I will need: PlaceRequest, PlaceResponse. Claude is suggesting: Enum for PlaceTypeEnum (restaurants, hospitals, etc.) and an AccessibilityPriorities class

class PlaceTypeEnum(str, Enum):
    restaurant = "restaurant"
    cafe = "cafe"
    dentist = "dentist"
    hospital = "hospital"
    pharmacy = "pharmacy"
    shopping_mall = "shopping_mall"
    gym = "gym"
    library = "library"

class AccessibilityPriorities(BaseModel):
    wheelchair_accessible_entrance: int = Field(default=3, ge=0, le=5)
    wheelchair_accessible_parking: int = Field(default=2, ge=0, le=5)
    wheelchair_accessible_restroom: int = Field(default=2, ge=0, le=5)
    wheelchair_accessible_seating: int = Field(default=1, ge=0, le=5)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    radius: float = Field(default=1000, ge=100, le=50000)
    place_type: PlaceTypeEnum
    accessibility_priorities: Optional[AccessibilityPriorities] = None

class PlaceResponse(BaseModel):
    display_name: Dict[str, str]
    formatted_address: Optional[str]
    location: Dict[str, float]
    rating: Optional[float]
    user_rating_count: Optional[int]
    accessibility_options: Optional[Dict[str, bool]]
    accessibility_score: float
    accessibility_status: str
    accessibility_breakdown: Dict[str, bool]

class GeocodeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)

class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float
    display_name: str

class Health(BaseModel):
    status: str
    version: str
    message: str