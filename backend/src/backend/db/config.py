import os
from typing import Any

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from tortoise import Tortoise
from tortoise.contrib.fastapi import (
    register_tortoise,  # type: ignore[reportUnknownVariableType, unused-ignore]
)


# Helper functions
def _get_sqlite_config(db_url: str) -> dict[str, Any]:
    """Convert a SQLite URL to a Tortoise ORM SQLite config."""
    if db_url == "sqlite://:memory:":
        # In-memory database
        return {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": ":memory:"},
        }
    else:
        # File-based database
        # Remove sqlite:// prefix to get the file path
        file_path = db_url.replace("sqlite://", "")
        return {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": file_path},
        }


class DatabaseSettings(BaseSettings):
    # Default database settings that can be overridden by environment variables
    DATABASE_URL: str = "postgres://localhost:5432/robot_overlord"
    DB_ENGINE: str = "postgres"
    TESTING: bool = False

    # Configure settings based on environment
    model_config = SettingsConfigDict(
        env_file=".env" if os.environ.get("TESTING") != "True" else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create a global instance of settings
db_settings = DatabaseSettings()


# Tortoise ORM configuration
def get_tortoise_config() -> dict[str, Any]:
    """Get Tortoise ORM configuration based on the database engine."""
    # Define the base configuration
    config = {
        "apps": {
            "models": {
                "models": (
                    ["backend.db.models"]
                    if db_settings.DB_ENGINE.lower() == "sqlite"
                    else ["backend.db.models", "aerich.models"]
                ),
                "default_connection": "default",
            },
        },
        "use_tz": True,
        "timezone": "UTC",
    }

    # Configure connections based on database engine
    connections: dict[str, Any] = {}

    if db_settings.DB_ENGINE.lower() == "sqlite":
        # For SQLite, use our helper function to create the proper configuration
        sqlite_config = _get_sqlite_config(db_settings.DATABASE_URL)
        connections["default"] = sqlite_config
    else:
        # For other databases, use the connection string directly
        connections["default"] = db_settings.DATABASE_URL

    config["connections"] = connections

    return config


# Get the configuration based on the current environment
TORTOISE_ORM: dict[str, Any] = get_tortoise_config()


async def init_db(db_url: str | None = None) -> None:
    # Create a copy of the config for runtime use
    config = TORTOISE_ORM.copy()

    # Override connection URL if provided
    if db_url:
        if db_settings.DB_ENGINE.lower() == "sqlite":
            # Use our helper function to create the SQLite config
            sqlite_config = _get_sqlite_config(db_url)

            # Type check to ensure we're not assigning to a string
            connections = config.get("connections", {})
            if isinstance(connections, dict):
                connections["default"] = sqlite_config
        else:
            config["connections"]["default"] = db_url

    await Tortoise.init(config=config)


async def close_db() -> None:
    await Tortoise.close_connections()


def init_tortoise(app: Any) -> None:
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,  # We'll use Aerich for migrations
        add_exception_handlers=True,
    )
