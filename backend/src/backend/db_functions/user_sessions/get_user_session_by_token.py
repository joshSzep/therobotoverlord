# Standard library imports
from typing import Optional

# Project-specific imports
from backend.converters.user_session_to_schema import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema


async def get_user_session_by_token(token: str) -> Optional[UserSessionSchema]:
    # Find the session by token
    query = UserSession.filter(session_token=token, is_active=True)
    session = await query.prefetch_related("user").first()

    if not session:
        return None

    # Convert to schema and return
    return await user_session_to_schema(session)
