# Standard library imports
from typing import Optional

# Project-specific imports
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.user import UserSchema


async def user_schema_to_response(
    user_schema: Optional[UserSchema],
) -> Optional[UserResponse]:
    if not user_schema:
        return None

    return UserResponse(
        id=user_schema.id,
        email=user_schema.email,
        display_name=user_schema.display_name,
        is_verified=user_schema.is_verified,
        last_login=user_schema.last_login,
        role=user_schema.role,
        is_locked=user_schema.is_locked,
        created_at=user_schema.created_at,
        updated_at=user_schema.updated_at,
        approved_count=user_schema.approved_count,
        rejected_count=user_schema.rejected_count,
    )
