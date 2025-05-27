# Standard library imports
from datetime import timedelta
import secrets
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.db.models.user_event import UserEvent
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSchema
from backend.utils.datetime import now_utc


async def record_login_success(
    user_id: UUID, ip_address: str, user_agent: str
) -> Optional[UserSchema]:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    # Update user fields
    user.last_login = now_utc()
    user.failed_login_attempts = 0
    user.is_locked = False
    await user.save()

    # Generate a session token
    session_token = secrets.token_hex(32)

    # Create a session record
    await UserSession.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        session_token=session_token,
        is_active=True,
        expires_at=now_utc() + timedelta(days=7),
    )

    # Record the login event
    await UserEvent.create(
        user=user,
        event_type="login",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={"success": True},
    )

    return await user_to_schema(user)
