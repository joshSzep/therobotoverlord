"""Session management background tasks."""

import asyncio
import logging

from tortoise import Tortoise

from backend.db.config import TORTOISE_ORM
from backend.db.models.user_session import UserSession
from backend.utils.settings import settings

logger = logging.getLogger(__name__)


async def cleanup_expired_sessions() -> int:
    """Clean up expired user sessions.

    This function is intended to be run as a background task.

    Returns:
        int: Number of sessions cleaned up.
    """
    # Initialize database connection if not already initialized
    if not Tortoise._inited:  # type: ignore[reportPrivateUsage, unused-ignore]
        await Tortoise.init(config=TORTOISE_ORM)

    try:
        # Cleanup expired sessions
        count = await UserSession.cleanup_expired()

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
    """Run the session cleanup task periodically.

    Args:
        interval_seconds: Interval between cleanup runs in seconds.
    """
    while True:
        await cleanup_expired_sessions()
        await asyncio.sleep(interval_seconds)
