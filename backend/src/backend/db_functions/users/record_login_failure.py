# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.db_functions.user_events.log_account_lockout import log_account_lockout
from backend.db_functions.user_events.log_login_failure import log_login_failure
from backend.schemas.user import UserSchema


async def record_login_failure(
    user_id: Optional[UUID], ip_address: str, user_agent: str
) -> Optional[UserSchema]:
    # If user_id is None, log the event and return None
    if not user_id:
        await log_login_failure(None, ip_address, user_agent)
        return None

    # Get user by id, if not found, log the event and return None
    user = await User.get_or_none(id=user_id)
    if not user:
        await log_login_failure(None, ip_address, user_agent)
        return None

    # We found the user, update their fields
    user.failed_login_attempts += 1

    # Lock account after 5 failed attempts
    was_locked = False
    if user.failed_login_attempts >= 5 and not user.is_locked:
        user.is_locked = True
        was_locked = True

    await user.save()

    # Record the login failure event
    await log_login_failure(
        user_id=user.id, ip_address=ip_address, user_agent=user_agent
    )

    # Log account lockout event if account was just locked
    if was_locked:
        await log_account_lockout(user.id, ip_address, user_agent)

    return await user_to_schema(user)
