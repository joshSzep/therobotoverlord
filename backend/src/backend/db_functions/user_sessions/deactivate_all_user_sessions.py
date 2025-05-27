# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.user_session import UserSession


async def deactivate_all_user_sessions(user_id: UUID) -> int:
    sessions = await UserSession.filter(user_id=user_id, is_active=True)
    count = 0

    for session in sessions:
        session.is_active = False
        await session.save()
        count += 1

    return count
