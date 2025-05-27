# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def lock_user_account(user_id: UUID) -> Optional[UserSchema]:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    user.is_locked = True
    await user.save()
    return await user_to_schema(user)
