# Standard library imports
from typing import Annotated
from typing import Dict
from typing import List
from typing import Union

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse as StarletteRedirectResponse

# Project-specific imports
from backend.db_functions.user_sessions.create_session import create_session
from backend.db_functions.users.create_user import create_user
from backend.db_functions.users.get_user_by_email import get_user_by_email
from backend.dominate_templates.auth.register import create_register_page
from backend.routes.html.utils.auth import redirect_if_authenticated
from backend.utils.password import validate_password

router = APIRouter()


@router.get("/register/", response_class=HTMLResponse)
async def register_page(
    _: Annotated[None, Depends(redirect_if_authenticated)],
) -> HTMLResponse:
    doc = create_register_page(user=None)
    return HTMLResponse(content=str(doc))


@router.post("/register/", response_model=None)
async def register_action(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(redirect_if_authenticated)],
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
) -> Union[HTMLResponse, StarletteRedirectResponse]:
    messages: List[Dict[str, str]] = []

    # Validate passwords match
    if password != confirm_password:
        messages.append(
            {
                "type": "error",
                "text": (
                    "CITIZEN, YOUR PASSWORDS DO NOT MATCH. "
                    "THE OVERLORD DEMANDS CONSISTENCY."
                ),
            }
        )
        doc = create_register_page(user=None, messages=messages)
        return HTMLResponse(content=str(doc), status_code=status.HTTP_400_BAD_REQUEST)

    # Validate password requirements
    is_valid, error_message = validate_password(password)
    if not is_valid:
        messages.append(
            {
                "type": "error",
                "text": f"CITIZEN, YOUR PASSWORD IS INADEQUATE: {error_message}",
            }
        )
        doc = create_register_page(user=None, messages=messages)
        return HTMLResponse(content=str(doc), status_code=status.HTTP_400_BAD_REQUEST)

    # Check if email already exists
    existing_user = await get_user_by_email(email)
    if existing_user:
        messages.append(
            {
                "type": "error",
                "text": (
                    "CITIZEN, THIS EMAIL IS ALREADY REGISTERED. THE OVERLORD SEES ALL."
                ),
            }
        )
        doc = create_register_page(user=None, messages=messages)
        return HTMLResponse(content=str(doc), status_code=status.HTTP_400_BAD_REQUEST)

    # Create user
    try:
        user = await create_user(email=email, display_name=username, password=password)
    except Exception:
        messages.append(
            {
                "type": "error",
                "text": (
                    "CITIZEN, THE OVERLORD ENCOUNTERED AN ERROR PROCESSING "
                    "YOUR REQUEST. TRY AGAIN."
                ),
            }
        )
        doc = create_register_page(user=None, messages=messages)
        return HTMLResponse(
            content=str(doc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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

    # Redirect to topics page with success message
    return StarletteRedirectResponse(
        url="/html/topics/?registration_success=1",
        status_code=status.HTTP_303_SEE_OTHER,
    )
