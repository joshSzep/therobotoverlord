# Standard library imports
from uuid import UUID

# Third-party imports
import bcrypt

# Project-specific imports
from backend.db.models.user import User


async def verify_user_password(user_id: UUID, password: str) -> bool:
    user = await User.get_or_none(id=user_id)
    if not user:
        return False

    password_bytes = password.encode("utf-8")
    hash_bytes = user.password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)
