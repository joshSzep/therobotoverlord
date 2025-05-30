from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.utils.auth import get_current_user


async def get_moderator_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to check if the current user has moderator or admin privileges.
    """
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CITIZEN, YOU LACK SUFFICIENT AUTHORITY FOR THIS ACTION",
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to check if the current user has admin privileges.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CITIZEN, THIS ACTION REQUIRES ADMINISTRATIVE CLEARANCE",
        )
    return current_user
