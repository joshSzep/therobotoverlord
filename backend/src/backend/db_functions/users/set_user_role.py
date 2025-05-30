from uuid import UUID

from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.schemas.user import UserSchema


async def set_user_role(
    user_id: UUID,
    role: UserRole,
) -> UserSchema | None:
    """
    Set a user's role.

    Args:
        user_id: The UUID of the user
        role: The new role to assign to the user

    Returns:
        Updated UserSchema or None if user not found
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    user.role = role
    await user.save()
    return await user_to_schema(user)
