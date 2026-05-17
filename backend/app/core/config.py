from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Accessibility Tracker"
    VERSION: str = "1.0.0"
    GOOGLE_MAPS_API_KEY: str


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
