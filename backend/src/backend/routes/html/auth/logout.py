# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Depends
from fastapi import Response
from fastapi import status
from fastapi.responses import RedirectResponse
from starlette.responses import RedirectResponse as StarletteRedirectResponse

# Project-specific imports
from backend.db_functions.user_sessions import delete_user_session
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user

router = APIRouter()


@router.get("/logout/", response_class=RedirectResponse)
async def logout_action(
    response: Response,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session_token: Annotated[str, Cookie()],
) -> StarletteRedirectResponse:
    # Delete session
    await delete_user_session(session_token)

    # Clear session cookie
    response.delete_cookie(key="session_token")

    # Redirect to home page
    return StarletteRedirectResponse(
        url="/html/",
        status_code=status.HTTP_303_SEE_OTHER,
    )
