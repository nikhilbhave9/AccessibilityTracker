from fastapi import FastAPI, Body
from typing import List, Dict
from app.apis.v1 import search
from app.core.config import config
from app.core.logging import setup_logging

from app.schemas.search import SearchRequest

from app.services.google_places import google_places

setup_logging()

app = FastAPI(title=config.app_name)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/search")
async def search(request: SearchRequest = Body(...)) -> List[Dict]:
    places = await google_places(request.latitude, request.longitude, request.radius, request.place_type)
    return places

# # Register routes
# app.include_router(user.router, prefix="/api/v1")