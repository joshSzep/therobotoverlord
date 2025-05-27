from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status

from backend.db.models.user import User  # Keep for type annotation
from backend.db_functions.user_events import log_logout
from backend.db_functions.user_sessions import deactivate_session
from backend.db_functions.user_sessions import list_user_sessions
from backend.utils.auth import get_current_user
from backend.utils.constants import UNKNOWN_IP_ADDRESS_MARKER

router = APIRouter()


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> None:
    # Get client information
    ip_address = request.client.host if request.client else UNKNOWN_IP_ADDRESS_MARKER
    user_agent = request.headers.get("User-Agent", "")

    # Find and invalidate active sessions for this user with the same IP and user agent
    sessions, _ = await list_user_sessions(
        user_id=current_user.id,
        active_only=True,
    )

    for session in sessions:
        if session.ip_address == ip_address and session.user_agent == user_agent:
            await deactivate_session(session.session_token)

    # Log logout event
    await log_logout(current_user.id, ip_address, user_agent)
