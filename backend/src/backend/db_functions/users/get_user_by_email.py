# Standard library imports
from typing import Optional

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def get_user_by_email(email: str) -> Optional[UserSchema]:
    user = await User.get_or_none(email=email)
    if user:
        return await user_to_schema(user)
    return None
