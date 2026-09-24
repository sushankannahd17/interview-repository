from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/interview_platform"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/interview_platform"
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    TEAM_B_API_KEY: str = "change-me-in-production"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    PAGE_SIZE_DEFAULT: int = 20
    PAGE_SIZE_MAX: int = 100


settings = Settings()
