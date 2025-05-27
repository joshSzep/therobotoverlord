# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.user import User


async def verify_user_password(user_id: UUID, password: str) -> bool:
    user = await User.get_or_none(id=user_id)
    if not user:
        return False

    return await user.verify_password(password)
