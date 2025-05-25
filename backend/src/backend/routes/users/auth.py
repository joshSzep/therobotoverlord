"""Authentication endpoints for user registration and login."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from backend.db.models.user import User
from backend.db.models.user_event import UserEvent
from backend.routes.users.models import TokenSchema
from backend.routes.users.models import UserCreateSchema
from backend.routes.users.models import UserSchema
from backend.utils.auth import create_access_token
from backend.utils.auth import create_refresh_token
from backend.utils.auth import verify_token

router = APIRouter()


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreateSchema) -> UserSchema:
    """Register a new user.

    Args:
        user_data: User registration data.

    Returns:
        The newly created user.

    Raises:
        HTTPException: If the email is already registered or the password is invalid.
    """
    # Check if email already exists
    existing_user = await User.get_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate password
    from backend.utils.password import validate_password

    is_valid, error_message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    # Create new user
    user = User(
        email=user_data.email,
        display_name=user_data.display_name,
    )

    # Set password (this will hash it)
    await user.set_password(user_data.password)

    # Save user to database
    await user.save()

    # Return user data (without password)
    return UserSchema(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_verified=user.is_verified,
        last_login=user.last_login,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenSchema)
async def login(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenSchema:
    """Authenticate a user and return access and refresh tokens.

    Args:
        request: The FastAPI request object.
        form_data: OAuth2 password request form data.

    Returns:
        Access and refresh tokens.

    Raises:
        HTTPException: If authentication fails.
    """
    # Get client information
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")

    # Find user by email
    user = await User.get_or_none(email=form_data.username)

    # Check if user exists and password is correct
    if not user or not await user.verify_password(form_data.password):
        # If user exists, record login failure
        if user:
            await user.record_login_failure(ip_address, user_agent)
            # Log the event
            await UserEvent.log_login_failure(user.id, ip_address, user_agent)
        else:
            # Log anonymous login failure
            await UserEvent.log_login_failure(None, ip_address, user_agent)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR CREDENTIALS REQUIRE CALIBRATION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR ACCOUNT HAS BEEN TEMPORARILY SUSPENDED FOR RECALIBRATION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record successful login
    await user.record_login_success(ip_address, user_agent)

    # Log the event
    await UserEvent.log_login_success(user.id, ip_address, user_agent)

    # Create token data
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }

    # Create access and refresh tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(request: Request, refresh_token: str) -> TokenSchema:
    """Refresh an access token using a refresh token.

    Args:
        request: The FastAPI request object.
        refresh_token: The refresh token.

    Returns:
        New access and refresh tokens.

    Raises:
        HTTPException: If the refresh token is invalid or expired.
    """
    # Verify the refresh token
    try:
        payload = verify_token(refresh_token)

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
