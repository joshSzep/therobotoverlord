# Standard library imports

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def create_user(email: str, password: str, display_name: str) -> UserSchema:
    user = await User.create(
        email=email,
        password_hash="",  # Temporary placeholder
        display_name=display_name,
    )
    await user.set_password(password)
    await user.save()
    return await user_to_schema(user)
