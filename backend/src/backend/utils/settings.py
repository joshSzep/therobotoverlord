from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgres://localhost:5432/robot_overlord"

    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: float = 30.0
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: float = 7.0

    # Application settings
    DEBUG: bool = False
    TESTING: bool = False

    # Session settings
    SESSION_CLEANUP_INTERVAL_SECONDS: float = 3600.0

    # AI moderation settings
    OPENAI_API_KEY: str = "sk-dummy-key-for-development"
    AI_MODERATION_ENABLED: bool = True
    AI_MODERATION_AUTO_APPROVE: bool = True
    AI_MODERATION_AUTO_REJECT: bool = True
    AI_MODERATION_CONFIDENCE_THRESHOLD: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Create a global instance of settings
settings = Settings()
