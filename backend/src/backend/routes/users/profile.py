"""User profile endpoints for retrieving and updating user data."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from backend.db.models.user import User
from backend.db.models.user_event import UserEvent
from backend.routes.users.models import PasswordChangeRequest
from backend.routes.users.models import UserSchema
from backend.utils.auth import get_current_user
from backend.utils.password import validate_password

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    """Get information about the currently authenticated user.

    Args:
        current_user: The current authenticated user.

    Returns:
        User information.
    """
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


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
) -> None:
    """Change the user's password.

    Args:
        request: The FastAPI request object.
        password_data: Current and new password.
        current_user: The current authenticated user.

    Raises:
        HTTPException: If the current password is incorrect or the new password is invalid.
    """
    # Verify current password
    if not await current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR CURRENT PASSWORD IS INCORRECT",
        )

    # Validate new password
    is_valid, error_message = validate_password(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CITIZEN, YOUR NEW PASSWORD REQUIRES CALIBRATION: {error_message}",
        )

    # Set new password
    await current_user.set_password(password_data.new_password)
    await current_user.save()

    # Get client information for event logging
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")

    # Log password change event
    await UserEvent.log_password_change(current_user.id, ip_address, user_agent)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> None:
    """Log out the current user by invalidating their session.

    This endpoint doesn't actually invalidate the JWT token (as that's not possible),
    but it marks the user's session as inactive in the database.

    Args:
        request: The FastAPI request object.
        current_user: The current authenticated user.
    """
    # Get client information
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")

    # Find and invalidate active sessions for this user with the same IP and user agent
    sessions = await current_user.sessions.filter(
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
    ).all()

    for session in sessions:
        await session.invalidate()

    # Log logout event
    await UserEvent.log_logout(current_user.id, ip_address, user_agent)
