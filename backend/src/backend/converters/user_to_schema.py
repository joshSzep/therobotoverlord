from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def user_to_schema(user: User) -> UserSchema:
    return UserSchema(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_verified=user.is_verified,
        role=user.role,
        is_locked=user.is_locked,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
    )
