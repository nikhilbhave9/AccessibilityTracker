from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    app_name: str = "Accessibility Tracker"
    GOOGLE_MAPS_API_KEY: str

config = Config()