# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
import bcrypt

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def set_user_password(user_id: UUID, password: str) -> Optional[UserSchema]:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    user.password_hash = hashed.decode("utf-8")

    await user.save()
    return await user_to_schema(user)
