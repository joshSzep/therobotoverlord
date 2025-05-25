from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from backend.db.models.user import User
from backend.db.models.user_event import UserEvent
from backend.routes.users.users_schemas import PasswordChangeRequestSchema
from backend.utils.auth import get_current_user
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER
from backend.utils.password import validate_password

router = APIRouter()


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: Request,
    password_data: PasswordChangeRequestSchema,
    current_user: User = Depends(get_current_user),
) -> None:
    """Change the user's password.

    Args:
        request: The FastAPI request object.
        password_data: Current and new password.
        current_user: The current authenticated user.

    Raises:
        HTTPException: If the current password is incorrect or the new password is
        invalid.
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
    ip_address = request.client.host if request.client else UNKNOWN_IP_ADDRESS_MARKER
    user_agent = request.headers.get("User-Agent", "")

    # Log password change event
    await UserEvent.log_password_change(current_user.id, ip_address, user_agent)
