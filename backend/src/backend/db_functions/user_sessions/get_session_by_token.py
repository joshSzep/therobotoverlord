# Standard library imports
from typing import Optional

# Project-specific imports
from backend.converters import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema


async def get_session_by_token(session_token: str) -> Optional[UserSessionSchema]:
    session = await UserSession.get_or_none(
        session_token=session_token,
        is_active=True,
    ).prefetch_related("user")

    if session:
        return await user_session_to_schema(session)
    return None
