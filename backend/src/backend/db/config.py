from typing import Any

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from tortoise import Tortoise
from tortoise.contrib.fastapi import (
    register_tortoise,  # type: ignore[reportUnknownVariableType, unused-ignore]
)


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgres://localhost:5432/robot_overlord"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Create a global instance of settings
db_settings = DatabaseSettings()

# Tortoise ORM configuration
TORTOISE_ORM: dict[str, Any] = {
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


async def init_db(db_url: str | None = None) -> None:
    # Create a copy of the config for runtime use
    config = TORTOISE_ORM.copy()

    # Override connection URL if provided
    if db_url:
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
