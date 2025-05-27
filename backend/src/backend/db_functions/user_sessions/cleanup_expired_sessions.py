# Standard library imports

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.utils.datetime import now_utc


async def cleanup_expired_sessions() -> int:
    """Deactivate all expired sessions."""
    current_time = now_utc()
    sessions = await UserSession.filter(is_active=True, expires_at__lt=current_time)
    count = 0

    for session in sessions:
        session.is_active = False
        await session.save()
        count += 1

    return count
