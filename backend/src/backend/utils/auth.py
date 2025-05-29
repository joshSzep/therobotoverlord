from datetime import timedelta
from typing import Any

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
import jwt

from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.utils.datetime import now_utc
from backend.utils.settings import settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
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
    to_encode = data.copy()
    expire = now_utc() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "refresh": True})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CITIZEN, YOUR AUTHENTICATION TOKEN HAS FAILED INSPECTION",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR AUTHENTICATION TOKEN HAS FAILED INSPECTION",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR IDENTITY DOCUMENTS REQUIRE VERIFICATION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get_or_none(id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN NOT FOUND IN STATE RECORDS",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="CITIZEN, YOUR ACCOUNT HAS BEEN LOCKED FOR RECALIBRATION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the user has an active session
    active_session = await UserSession.filter(
        user_id=user_id,
        is_active=True,
    ).exists()

    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR SESSION HAS EXPIRED OR BEEN TERMINATED",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    token: str | None = Depends(oauth2_scheme),
) -> User | None:
    if token is None:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None
