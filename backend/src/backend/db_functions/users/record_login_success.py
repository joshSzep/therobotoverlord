# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.db_functions.user_events import log_login_success
from backend.db_functions.user_sessions import create_session
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

    # Create a session record
    _ = await create_session(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Record the login success event
    _ = await log_login_success(user_id, ip_address, user_agent)

    return await user_to_schema(user)
