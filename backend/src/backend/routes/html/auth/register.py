# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse as StarletteRedirectResponse

# Project-specific imports
from backend.db_functions.user_sessions.create_session import create_session
from backend.db_functions.users.create_user import create_user
from backend.routes.html.utils.auth import redirect_if_authenticated

router = APIRouter()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/backend/templates")


@router.get("/register/", response_class=HTMLResponse)
async def register_page(
    request: Request,
    _: Annotated[None, Depends(redirect_if_authenticated)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        "pages/auth/register.html",
        {
            "request": request,
            "user": None,
        },
    )


@router.post("/register/", response_class=RedirectResponse)
async def register_action(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(redirect_if_authenticated)],
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
) -> StarletteRedirectResponse:
    # Validate passwords match
    if password != confirm_password:
        # In a real application, you'd want to show an error message
        return StarletteRedirectResponse(
            url="/html/auth/register/",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Create user
    try:
        user = await create_user(email=email, display_name=username, password=password)
    except Exception:
        # In a real application, you'd want to show an error message
        return StarletteRedirectResponse(
            url="/html/auth/register/",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Create session
    session = await create_session(
        user_id=user.id,
        ip_address=request.client.host if request.client else "127.0.0.1",
        user_agent=request.headers.get("user-agent", ""),
    )

    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        secure=True,
        samesite="lax",
    )

    # Redirect to home page
    return StarletteRedirectResponse(
        url="/html/",
        status_code=status.HTTP_303_SEE_OTHER,
    )
