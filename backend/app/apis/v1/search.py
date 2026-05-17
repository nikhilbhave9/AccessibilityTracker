from typing import Annotated, List

from fastapi import APIRouter, Query
from app.schemas.search import Health, GeocodeRequest, GeocodeResponse, SearchRequest, PlaceResponse, AccessibilityPriorities
from app.core.config import settings
from app.services import geocoding
from app.services.google_places import google_places_service

router = APIRouter()

@router.post("/search", response_model = List[PlaceResponse])
async def search(request: SearchRequest):
    """
    Search for accessible places near a location
    
    Example request:
    {
        "latitude": 18.5089,
        "longitude": 73.7697,
        "radius": 1000,
        "place_type": "restaurant",
        "accessibility_priorities": {
            "wheelchair_accessible_entrance": 3,
            "wheelchair_accessible_parking": 2,
            "wheelchair_accessible_restroom": 2,
            "wheelchair_accessible_seating": 1
        }
    }

    Example response:
    [
        {
            "display_name": "Restaurant 1",
            "formatted_address": "123 Main St, Anytown, USA",
            "location": {
                "latitude": 18.5089,
                "longitude": 73.7697
            },
            "rating": 4.5,
            "user_rating_count": 100,
            "accessibility_options": {
                "wheelchair_accessible_entrance": True,
                "wheelchair_accessible_parking": True,
                "wheelchair_accessible_restroom": True,
                "wheelchair_accessible_seating": True
            },
            "accessibility_score": 8.5,
            "accessibility_status": "excellent",
            "accessibility_breakdown": {
                "wheelchair_accessible_entrance": True,
                "wheelchair_accessible_parking": True,
                "wheelchair_accessible_restroom": True,
                "wheelchair_accessible_seating": True
            }
        }
    ]
    """
    # Set default priorities if not provided
    if request.accessibility_priorities is None:
        request.accessibility_priorities = AccessibilityPriorities()
    
    # Geocode the location
    location = await geocoding.geocode(f"{request.query}")
    request.latitude = location["latitude"]
    request.longitude = location["longitude"]
    request.query = location["display_name"]

    # Search for places
    places = await google_places_service.search_places(
        latitude=request.latitude,
        longitude=request.longitude,
        radius=request.radius,
        place_type=request.place_type
    )
    accessible_places = []


@router.get("/geocode", response_model = GeocodeResponse)
async def geocode(
    params: Annotated[GeocodeRequest, Query()],
):
    """
    Geocode a location using Nominatim API (OpenStreetMap)
    """
    result = await geocoding.geocode(params.query)
    return GeocodeResponse(
        latitude=result["latitude"],
        longitude=result["longitude"],
        display_name=result["display_name"]
    )


@router.get("/health", response_model = Health)
async def health_check():
    return Health(
        status="healthy",
        version=settings.VERSION,
        message="Accessibility Tracker API is running and ready to serve requests."
    )
