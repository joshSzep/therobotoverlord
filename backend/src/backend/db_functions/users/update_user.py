# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def update_user(
    user_id: UUID,
    display_name: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[UserSchema]:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    if display_name:
        user.display_name = display_name

    if email:
        user.email = email

    await user.save()
    return await user_to_schema(user)
