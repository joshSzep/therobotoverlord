# Standard library imports
from typing import Optional

# Third-party imports
import bcrypt

from backend.converters.user_schema_to_response import user_schema_to_response
from backend.converters.user_to_schema import user_to_schema

# Project-specific imports
from backend.db.models.user import User
from backend.routes.html.schemas.user import UserResponse


async def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
    # Find user by email
    user = await User.filter(email=email).first()
    if not user:
        return None

    # Check password
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None

    # Convert user model to schema then to response
    user_schema = await user_to_schema(user)
    return await user_schema_to_response(user_schema)
