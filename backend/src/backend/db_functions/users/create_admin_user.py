# Standard library imports

# Project-specific imports
from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.db_functions.users.set_user_password import set_user_password
from backend.schemas.user import UserSchema


async def create_admin_user(email: str, password: str, display_name: str) -> UserSchema:
    """Create a new user with admin role."""
    user = await User.create(
        email=email,
        password_hash="",  # Temporary placeholder
        display_name=display_name,
        role=UserRole.ADMIN,
        is_verified=True,  # Admin users are automatically verified
    )
    result = await set_user_password(user.id, password)
    if result is None:
        # This should never happen since we just created the user
        raise ValueError(f"Failed to set password for user {user.id}")
    return result
