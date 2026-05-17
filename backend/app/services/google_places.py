import requests
from typing import List, Dict
from app.core.config import settings
from fastapi import HTTPException
from app.schemas.place import AccessibilityScore
from app.schemas.search import AccessibilityPriorities

class GooglePlacesService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchNearby"

    async def search_places(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        place_type: str
    ) -> List[Dict]:
            """
            Search for places nearby a given location
            """
            url = f"{self.base_url}"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": (
                    "places.displayName,"
                    "places.formattedAddress,"
                    "places.location,"
                    "places.accessibilityOptions,"
                    "places.rating,"
                    "places.userRatingCount"
                )
            }
            payload = {
                "includedTypes": [place_type],
                "maxResultCount": 20,
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": latitude,
                            "longitude": longitude,
                        },
                        "radius": radius,
                    },
                },
            }
            try: 
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json().get("places", [])
            except requests.exceptions.RequestException as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling Google Places API: {str(e)}"
                )
        
    async def get_accessibility_score(
        self,
        accessibility_options: Dict[str, bool],
        accessibility_priorities: AccessibilityPriorities
    ) -> AccessibilityScore:
        """
        Get the accessibility score for a place
        """
        if not accessibility_options:
            return AccessibilityScore(
                score=0.0,
                status="no_data",
                breakdown={}
            )
        
        priority_weights = accessibility_priorities.model_dump()
        total_weight = sum(priority_weights.values())
        
        if total_weight == 0:
            return AccessibilityScore(
                score=0.0,
                status="no_data",
                breakdown={}
            )
        
        earned_points = 0
        for feature, weight in priority_weights.items():
            if accessibility_options.get(feature, False):
                earned_points += weight
        
        # Normalize score to 0-10 scale
        score = (earned_points / total_weight) * 10
        score = round(score, 1)

        # Determine status
        if score >= 7:
            status = "excellent"
        elif score >= 4:
            status = "partial"
        elif score >= 0:
            status = "limited"
        else:
            status = "no_data"

        # Create breakdown
        breakdown = {
            feature: accessibility_options.get(feature, False)
            for feature in priority_weights.keys()
        }

        return AccessibilityScore(
            score=score,
            status=status,
            breakdown=breakdown
        )

google_places_service = GooglePlacesService()