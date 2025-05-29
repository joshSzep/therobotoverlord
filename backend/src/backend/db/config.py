import os
from typing import Any

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from tortoise import Tortoise
from tortoise.contrib.fastapi import (
    register_tortoise,  # type: ignore[reportUnknownVariableType, unused-ignore]
)


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgres://localhost:5432/robot_overlord"
    DB_ENGINE: str = "postgres"  # Default to postgres, can be overridden to 'sqlite'
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
    config = {
        "connections": {"default": db_settings.DATABASE_URL},
        "apps": {
            "models": {
                "models": ["backend.db.models", "aerich.models"],
                "default_connection": "default",
            },
        },
        "use_tz": True,
        "timezone": "UTC",
    }

    # For SQLite, we need to add some special configuration
    if db_settings.DB_ENGINE.lower() == "sqlite":
        # Remove aerich from models for SQLite (not needed for tests)
        apps = config.get("apps", {})
        if isinstance(apps, dict):
            models_config = apps.get("models", {})
            if isinstance(models_config, dict) and "models" in models_config:
                models_config["models"] = ["backend.db.models"]

        # Add SQLite-specific configuration
        connections = config.get("connections", {})
        if isinstance(connections, dict):
            # Create the SQLite connection config
            # Handle SQLite URL format
            db_url = db_settings.DATABASE_URL

            # Extract the file path from the SQLite URL
            # Handle different URL formats:
            # - sqlite://:memory: -> :memory:
            # - sqlite://./path/to/file.db -> ./path/to/file.db
            # - sqlite:///absolute/path/to/file.db -> /absolute/path/to/file.db
            sqlite_config: dict[str, Any]

            if db_url == "sqlite://:memory:":
                # In-memory database
                sqlite_config = {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file": ":memory:"},
                }
            else:
                # File-based database
                # Remove sqlite:// prefix to get the file path
                file_path = db_url.replace("sqlite://", "")

                # Ensure the file path is valid
                sqlite_config = {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file": file_path},
                }
            # Assign it to the connections dictionary
            # We need to replace the string connection with our SQLite config
            # First, create a new connections dict with our SQLite config
            new_connections = {"default": sqlite_config}
            # Then update the config with the new connections
            config["connections"] = new_connections

    return config


# Get the configuration based on the current environment
TORTOISE_ORM: dict[str, Any] = get_tortoise_config()


async def init_db(db_url: str | None = None) -> None:
    # Create a copy of the config for runtime use
    config = TORTOISE_ORM.copy()

    # Override connection URL if provided
    if db_url:
        if db_settings.DB_ENGINE.lower() == "sqlite":
            # Handle SQLite URL format
            if db_url == "sqlite://:memory:":
                # In-memory database
                # Type check to ensure we're not assigning to a string
                connections = config.get("connections", {})
                if isinstance(connections, dict):
                    connections["default"] = {
                        "engine": "tortoise.backends.sqlite",
                        "credentials": {"file": ":memory:"},
                    }
            else:
                # File-based database
                # Remove sqlite:// prefix to get the file path
                file_path = db_url.replace("sqlite://", "")

                # Type check to ensure we're not assigning to a string
                connections = config.get("connections", {})
                if isinstance(connections, dict):
                    connections["default"] = {
                        "engine": "tortoise.backends.sqlite",
                        "credentials": {"file": file_path},
                    }
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
