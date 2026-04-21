from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.apis.v1 import search
from app.core.logging import setup_logging

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

app.include_router(search.router, prefix="/api/v1", tags=["Health"])

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}