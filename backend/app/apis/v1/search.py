from fastapi import APIRouter
from app.schemas.search import Health, GeocodeRequest, GeocodeResponse
from app.core.config import settings
from app.services import geocoding

router = APIRouter()

@router.post("/geocode", response_model = GeocodeResponse)
async def geocode(request: GeocodeRequest):
    """
    Convert a location name into geocoded coordinates (lat, long) plus a display name
    """
    result = await geocoding.geocode(request.query)
    return GeocodeResponse(**result)

@router.get("/health", response_model = Health)
async def health_check():
    return Health(
        status="healthy",
        version=settings.VERSION,
        message="Accessibility Tracker API is running and ready to serve requests."
    )
