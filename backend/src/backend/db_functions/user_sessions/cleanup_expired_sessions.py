# Standard library imports

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.utils.datetime import now_utc


async def cleanup_expired_sessions() -> int:
    """Deactivate all expired sessions."""
    count = await UserSession.filter(
        expires_at__lt=now_utc(),
        is_active=True,
    ).update(is_active=False)
    return count
