# Standard library imports
import logging
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from starlette.responses import RedirectResponse as StarletteRedirectResponse

# Project-specific imports
from backend.db_functions.user_sessions.create_session import create_session
from backend.db_functions.users.authenticate_user import authenticate_user
from backend.dominate_templates.auth.login import create_login_page
from backend.routes.html.utils.auth import redirect_if_authenticated

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/login/", response_class=HTMLResponse)
async def login_page(
    _: Annotated[None, Depends(redirect_if_authenticated)],
) -> HTMLResponse:
    doc = create_login_page(user=None)
    return HTMLResponse(content=str(doc))


@router.post("/login/", response_class=RedirectResponse)
async def login_action(
    request: Request,
    _: Annotated[None, Depends(redirect_if_authenticated)],
    email: str = Form(...),
    password: str = Form(...),
) -> StarletteRedirectResponse:
    # Authenticate user
    user = await authenticate_user(email, password)
    if not user:
        # In a real application, you'd want to show an error message
        return StarletteRedirectResponse(
            url="/html/auth/login/",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Create session
    session = await create_session(
        user_id=user.id,
        ip_address=request.client.host if request.client else "127.0.0.1",
        user_agent=request.headers.get("user-agent", ""),
    )

    logger.debug("Created session with token: %s", session.session_token)

    # Create redirect response
    redirect = StarletteRedirectResponse(
        url="/html/",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    # Set cookie directly on the redirect response
    redirect.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        # Don't use secure=True in development environment
        secure=False,
        samesite="lax",
        path="/",  # Make cookie available for the entire site
    )

    logger.debug("Set cookie on response: session_token=%s", session.session_token)

    # Return the redirect with the cookie
    return redirect
