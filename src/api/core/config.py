from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "FindArtisan API"
    PROJECT_DESCRIPTION: str = (
        "Helps clients find skilled artisans nearby and request their services."
    )
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
