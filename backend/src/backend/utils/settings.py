from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global instance of settings
settings = Settings()
