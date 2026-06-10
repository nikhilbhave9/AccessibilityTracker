from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.apis.v1 import search
from app.core.logging import setup_logging
from app.schemas.search import Health

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}


@app.get("/health", response_model=Health, tags=["Health"])
async def health_check_root():
    """Alias for GET /api/v1/health (same payload)."""
    return Health(
        status="healthy",
        version=settings.VERSION,
        message="Accessibility Tracker API is running and ready to serve requests.",
    )