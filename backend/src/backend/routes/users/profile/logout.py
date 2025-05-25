from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status

from backend.db.models.user import User
from backend.db.models.user_event import UserEvent
from backend.utils.auth import get_current_user
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER

router = APIRouter()


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
    ip_address = request.client.host if request.client else UNKNOWN_IP_ADDRESS_MARKER
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
