from fastapi import FastAPI

from app.apis.v1 import result
from app.core.config import config
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title=config.app_name)

# Register routes
app.include_router(user.router, prefix="/api/v1")