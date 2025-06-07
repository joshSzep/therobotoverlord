# Standard library imports

# Third-party imports
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.utils.auth import get_current_user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the current user is an admin.
    Raises an HTTP 403 exception if the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CITIZEN, THIS ACTION REQUIRES ADMINISTRATIVE CLEARANCE",
        )
    return current_user
