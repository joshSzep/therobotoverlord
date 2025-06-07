# Standard library imports
from typing import cast
from uuid import UUID

# Third-party imports
# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema


async def user_session_to_schema(session: UserSession) -> UserSessionSchema:
    # Ensure the user relationship is loaded
    if not hasattr(session, "user") or session.user is None:
        # If the session is from the database and user isn't prefetched
        await session.fetch_related("user")

    return UserSessionSchema(
        id=session.id,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        session_token=session.session_token,
        expires_at=session.expires_at,
        is_active=session.is_active,
        created_at=session.created_at,
        user_id=cast(UUID, session.user.id),
    )
