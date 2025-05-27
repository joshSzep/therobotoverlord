# Standard library imports
from typing import List
from typing import Tuple

# Project-specific imports
from backend.converters import user_to_schema
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def list_users(skip: int = 0, limit: int = 20) -> Tuple[List[UserSchema], int]:
    # Get total count for pagination
    count = await User.all().count()

    # Apply pagination
    users = await User.all().offset(skip).limit(limit)

    # Convert ORM models to schema objects using async converter
    user_schemas: List[UserSchema] = []
    for user in users:
        user_schemas.append(await user_to_schema(user))

    return user_schemas, count
