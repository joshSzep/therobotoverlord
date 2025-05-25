from fastapi import APIRouter
from fastapi import Depends

from backend.db.models.user import User
from backend.routes.users.users_schemas import UserSchema
from backend.utils.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    return UserSchema(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_verified=current_user.is_verified,
        last_login=current_user.last_login,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
