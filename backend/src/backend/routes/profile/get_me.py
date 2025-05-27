from fastapi import APIRouter
from fastapi import Depends

from backend.converters import user_to_schema
from backend.db.models.user import User  # Keep for type annotation
from backend.schemas.user import UserSchema
from backend.utils.auth import get_current_user

router = APIRouter()


@router.get("/me/", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    return await user_to_schema(current_user)
