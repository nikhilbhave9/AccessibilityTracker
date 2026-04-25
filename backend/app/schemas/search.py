from pydantic import BaseModel, Field

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