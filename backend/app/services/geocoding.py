import requests
from fastapi import HTTPException

NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"

async def geocode(query: str) -> dict:
    """
    Geocode a location using Nominatim API (OpenStreetMap)

    Args:
        query: The location to geocode (eg: Connaught Place, Delhi)

    Returns:
        Dict with latitude, longitude, display_name
    """
    url = f"{NOMINATIM_BASE_URL}/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }
    headers = {
        "User-Agent": "AccessibilityTracker/1.0)"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()

        if not results:
            raise HTTPException(
                status_code=404, 
                detail=f"Location {query} not found"
            )
        return {
            "latitude": float(results[0]["lat"]),
            "longitude": float(results[0]["lon"]),
            "display_name": results[0]["display_name"],
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error geocoding location {query}: {str(e)}"
        )