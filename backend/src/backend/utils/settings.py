"""Settings module for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    These settings can be configured via environment variables.
    """

    # Database settings
    DATABASE_URL: str = "postgres://localhost:5432/robot_overlord"

    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application settings
    DEBUG: bool = False
    TESTING: bool = False

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global instance of settings
settings = Settings()
