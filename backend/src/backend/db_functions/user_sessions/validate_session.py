# Standard library imports
from typing import Optional

# Project-specific imports
from backend.converters import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema
from backend.utils.datetime import now_utc


async def validate_session(session_token: str) -> Optional[UserSessionSchema]:
    # Get the raw session model first to check expiration and update if needed
    session = await UserSession.get_or_none(
        session_token=session_token,
        is_active=True,
    ).prefetch_related("user")

    if not session:
        return None

    # Check if session is expired
    if session.expires_at < now_utc():
        session.is_active = False
        await session.save()
        return None

    return await user_session_to_schema(session)
