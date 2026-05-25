from typing import Annotated, List

from fastapi import APIRouter, Query
from app.schemas.search import (
    Health,
    GeocodeRequest,
    GeocodeResponse,
    SearchRequest,
    PlaceResponse,
    AccessibilityPriorities,
)
from app.core.config import settings
from app.services import geocoding
from app.services.google_places import google_places_service
from app.services.nearby_place_normalize import normalize_nearby_places

router = APIRouter(tags=["Search"])


@router.post("/search", response_model=List[PlaceResponse])
async def search(body: SearchRequest):
    """
    Search for accessible places near a location (geocoded from query).

    Example request:
    {
        "query": "Baner, Pune",
        "radius": 1500,
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
            "display_name": {"text": "Sante Spa Cuisine", "languageCode": "en"},
            "formatted_address": "Erawati Bangla, Shrinath Nagar, Baner, Pune, Maharashtra 411069, India",
            "location": {"latitude": 18.5639122, "longitude": 73.7747798},
            "rating": 4.5,
            "user_rating_count": 796,
            "accessibility_options": {
                "wheelchair_accessible_parking": true,
                "wheelchair_accessible_entrance": true,
                "wheelchair_accessible_restroom": false,
                "wheelchair_accessible_seating": true
            },
            "accessibility_score": 7.5,
            "accessibility_status": "excellent",
            "accessibility_breakdown": {
                "wheelchair_accessible_entrance": true,
                "wheelchair_accessible_parking": true,
                "wheelchair_accessible_restroom": false,
                "wheelchair_accessible_seating": true
            }
        }
    ]

    Returns places with accessibility_score > 0, sorted by score then rating.
    """
    priorities = body.accessibility_priorities or AccessibilityPriorities()

    location = await geocoding.geocode(body.query)
    places = await google_places_service.search_places(
        latitude=location["latitude"],
        longitude=location["longitude"],
        radius=body.radius,
        place_type=body.place_type.value,
    )

    results: List[PlaceResponse] = []
    for normalized in normalize_nearby_places(places):
        score_result = await google_places_service.get_accessibility_score(
            normalized["accessibility_options"] or {},
            priorities,
        )

        display_name = {"text": normalized.get("name") or "Unknown"}
        if normalized.get("language_code"):
            display_name["languageCode"] = normalized["language_code"]

        results.append(PlaceResponse(
            display_name=display_name,
            formatted_address=normalized.get("formatted_address"),
            location={
                "latitude": normalized["latitude"],
                "longitude": normalized["longitude"],
            },
            rating=normalized.get("rating"),
            user_rating_count=normalized.get("user_rating_count"),
            accessibility_options=normalized.get("accessibility_options"),
            accessibility_score=score_result.score,
            accessibility_status=score_result.status,
            accessibility_breakdown=score_result.breakdown,
        ))

    filtered = [p for p in results if p.accessibility_score > 0]
    return sorted(
        filtered,
        key=lambda p: (p.accessibility_score, p.rating or 0),
        reverse=True,
    )


@router.get("/geocode", response_model=GeocodeResponse)
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
        display_name=result["display_name"],
    )


@router.get("/health", response_model=Health)
async def health_check():
    return Health(
        status="healthy",
        version=settings.VERSION,
        message="Accessibility Tracker API is running and ready to serve requests.",
    )
