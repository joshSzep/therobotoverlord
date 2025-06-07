# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import Cookie
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

# Project-specific imports
from backend.converters.user_schema_to_response import user_schema_to_response
from backend.db_functions.user_sessions.get_user_session_by_token import (
    get_user_session_by_token,
)
from backend.db_functions.users.get_user_by_id import get_user_by_id
from backend.routes.html.schemas.user import UserResponse


async def get_current_user_optional(
    request: Request, session_token: Annotated[str | None, Cookie()] = None
) -> UserResponse | None:
    if not session_token:
        return None

    # Get user session
    user_session = await get_user_session_by_token(session_token)
    if not user_session:
        return None

    # Get user by ID from the user_session
    user_schema = await get_user_by_id(user_session.user_id)

    # Convert UserSchema to UserResponse
    return await user_schema_to_response(user_schema)


async def get_current_user(
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
) -> UserResponse:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return current_user


def redirect_if_authenticated(
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
) -> None:
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/html/"},
        )


def redirect_if_not_authenticated(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    return current_user
