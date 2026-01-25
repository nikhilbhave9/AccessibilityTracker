from pydantic_settings import BaseSettings

class Config(BaseSettings):
    app_name: str = "Accessibility Tracker"
    GOOGLE_MAPS_API_KEY: str

config = Config()