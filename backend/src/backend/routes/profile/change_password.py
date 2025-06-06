from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from backend.db.models.user import User  # Keep for type annotation
from backend.db_functions.user_events import log_password_change
from backend.db_functions.users import set_user_password
from backend.db_functions.users import verify_user_password
from backend.schemas.password import PasswordChangeRequestSchema
from backend.utils.auth import get_current_user
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER
from backend.utils.password import validate_password

router = APIRouter()


@router.post("/change-password/", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: Request,
    password_data: PasswordChangeRequestSchema,
    current_user: User = Depends(get_current_user),
) -> None:
    # Verify current password using data access function
    if not await verify_user_password(current_user.id, password_data.current_password):
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

    # Set new password using data access function
    await set_user_password(current_user.id, password_data.new_password)

    # Get client information for event logging
    ip_address = request.client.host if request.client else UNKNOWN_IP_ADDRESS_MARKER
    user_agent = request.headers.get("User-Agent", "")

    # Log password change event
    await log_password_change(current_user.id, ip_address, user_agent)
