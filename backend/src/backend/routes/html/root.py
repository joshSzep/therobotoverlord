# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status
from starlette.responses import RedirectResponse

# Project-specific imports
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

router = APIRouter()


@router.get("/", response_class=RedirectResponse)
async def root_redirect(
    request: Request,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
) -> RedirectResponse:
    """
    Root HTML route that redirects to the topics page.
    """
    return RedirectResponse(url="/html/topics/", status_code=status.HTTP_302_FOUND)
