from datetime import timedelta
from typing import Any

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
import jwt

from backend.db.models.user import User
from backend.utils.datetime import now_utc
from backend.utils.settings import settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        data: The data to encode in the token.
        expires_delta: Optional expiration time. If not provided, the default
            expiration time from settings will be used.

    Returns:
        The encoded JWT token as a string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = now_utc() + expires_delta
    else:
        expire = now_utc() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token.

    Args:
        data: The data to encode in the token.

    Returns:
        The encoded JWT refresh token as a string.
    """
    to_encode = data.copy()
    expire = now_utc() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "refresh": True})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """Verify a JWT token and return its payload.

    Args:
        token: The JWT token to verify.

    Returns:
        The decoded token payload as a dictionary.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from the token.

    Args:
        token: The JWT token from the request.

    Returns:
        The authenticated user as a User object.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    payload = verify_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get_or_none(id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is locked. Please contact an administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    token: str | None = Depends(oauth2_scheme),
) -> User | None:
    """Get the current user if authenticated, or None if not.

    This dependency can be used for endpoints that allow anonymous access
    but provide additional functionality for authenticated users.

    Args:
        token: The JWT token from the request, if available.

    Returns:
        The authenticated user or None if the token is invalid.
    """
    if token is None:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None
