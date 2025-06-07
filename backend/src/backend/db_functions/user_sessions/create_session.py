# Standard library imports
from datetime import timedelta
import secrets
from uuid import UUID

# Project-specific imports
from backend.converters import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema
from backend.utils.datetime import now_utc


async def create_session(
    user_id: UUID,
    ip_address: str,
    user_agent: str,
    expires_in_days: int = 7,
) -> UserSessionSchema:
    session_token = secrets.token_hex(32)

    session = await UserSession.create(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        session_token=session_token,
        is_active=True,
        expires_at=now_utc() + timedelta(days=expires_in_days),
    )

    # Explicitly fetch the user relationship before converting
    await session.fetch_related("user")

    return await user_session_to_schema(session)
