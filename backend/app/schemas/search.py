from pydantic import BaseModel

class SearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float
    place_type: str
# Switch to Field() later for validation

# class SearchResponse(BaseModel):
#     places: list[Place]