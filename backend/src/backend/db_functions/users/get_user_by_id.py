# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def get_user_by_id(user_id: UUID) -> Optional[UserSchema]:
    user = await User.get_or_none(id=user_id)
    if user:
        return await user_to_schema(user)
    return None
