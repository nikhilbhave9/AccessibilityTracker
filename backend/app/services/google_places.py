import requests
from typing import List, Dict
from app.core.config import config


async def google_places(
    latitude: float,
    longitude: float,
    radius: float,
    place_type: str
) -> List[Dict]:

    url = 'https://places.googleapis.com/v1/places:searchNearby'
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': config.GOOGLE_MAPS_API_KEY,
        'X-Goog-FieldMask': 'places.displayName,places.accessibilityOptions'
    }

    json_data = {
        'includedTypes': [
            place_type,
        ],
        'maxResultCount': 20,
        'locationRestriction': {
            'circle': {
                'center': {
                    'latitude': latitude,
                    'longitude': longitude,
                },
                'radius': radius,
            },
        },
    }

    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()

    return response.json().get('places', [])

