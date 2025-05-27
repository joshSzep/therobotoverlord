# Standard library imports

# Project-specific imports
from backend.db.models.user_session import UserSession


async def deactivate_session(session_token: str) -> bool:
    session = await UserSession.get_or_none(session_token=session_token)
    if not session:
        return False

    session.is_active = False
    await session.save()
    return True
