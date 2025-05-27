# Standard library imports
import asyncio
import logging

# Third-party imports
from tortoise import Tortoise

# Project-specific imports
from backend.db.config import TORTOISE_ORM
from backend.db_functions.user_sessions.cleanup_expired_sessions import (
    cleanup_expired_sessions as db_cleanup_expired_sessions,
)
from backend.utils.settings import settings

logger = logging.getLogger(__name__)


async def cleanup_expired_sessions() -> int:
    # Initialize database connection if not already initialized
    if not Tortoise._inited:  # type: ignore[reportPrivateUsage, unused-ignore]
        await Tortoise.init(config=TORTOISE_ORM)

    try:
        # Cleanup expired sessions using the db_functions implementation
        count = await db_cleanup_expired_sessions()

        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")

        return count

    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        return 0

    finally:
        # Close database connection if we initialized it
        if Tortoise._inited:  # type: ignore[reportPrivateUsage, unused-ignore]
            await Tortoise.close_connections()


async def run_session_cleanup_task(
    interval_seconds: float = settings.SESSION_CLEANUP_INTERVAL_SECONDS,
) -> None:
    while True:
        await cleanup_expired_sessions()
        await asyncio.sleep(interval_seconds)
