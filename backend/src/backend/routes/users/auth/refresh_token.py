from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from backend.db.models.user import User
from backend.routes.users.users_schemas import TokenSchema
from backend.utils.auth import create_access_token
from backend.utils.auth import create_refresh_token
from backend.utils.auth import decode_token

router = APIRouter()


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(request: Request, refresh_token: str) -> TokenSchema:
    try:
        payload = decode_token(refresh_token)

        # Check if it's actually a refresh token
        if not payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get the user
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if account is locked
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }

        # Create new access and refresh tokens
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return TokenSchema(
            access_token=new_access_token,
            token_type="bearer",
            refresh_token=new_refresh_token,
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
