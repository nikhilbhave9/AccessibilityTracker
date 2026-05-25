"""Normalize Google Places API (New) nearby `places[]` entries for app code."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Field mask uses camelCase; AccessibilityPriorities uses snake_case.
_GOOGLE_TO_APP_A11Y = (
    ("wheelchairAccessibleParking", "wheelchair_accessible_parking"),
    ("wheelchairAccessibleEntrance", "wheelchair_accessible_entrance"),
    ("wheelchairAccessibleRestroom", "wheelchair_accessible_restroom"),
    ("wheelchairAccessibleSeating", "wheelchair_accessible_seating"),
)


def normalize_nearby_place(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten display name / location and map accessibilityOptions to snake_case.

    If Google omits `accessibilityOptions` or sends `{}`, `accessibility_options`
    is None (unknown — do not treat as “all false” for ranking).
    """
    raw_a11y = place.get("accessibilityOptions")
    accessibility_options: Optional[Dict[str, bool]]
    if not raw_a11y:
        accessibility_options = None
    else:
        accessibility_options = {
            snake: bool(raw_a11y.get(camel, False))
            for camel, snake in _GOOGLE_TO_APP_A11Y
        }

    display = place.get("displayName") or {}
    loc = place.get("location") or {}

    return {
        "name": display.get("text"),
        "language_code": display.get("languageCode"),
        "formatted_address": place.get("formattedAddress"),
        "latitude": loc.get("latitude"),
        "longitude": loc.get("longitude"),
        "rating": place.get("rating"),
        "user_rating_count": place.get("userRatingCount"),
        "accessibility_options": accessibility_options,
    }


def normalize_nearby_places(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_nearby_place(p) for p in places]
