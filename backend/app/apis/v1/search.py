from fastapi import APIRouter
from app.schemas.search import Health
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model = Health)
async def health_check():
    return Health(
        status="healthy",
        version=settings.VERSION,
        message="Accessibility Tracker API is running and ready to serve requests."
    )
