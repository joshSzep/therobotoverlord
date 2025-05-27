from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from backend.repositories.user_event_repository import UserEventRepository
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import TokenSchema
from backend.schemas.user import UserLoginSchema
from backend.utils.auth import create_access_token
from backend.utils.auth import create_refresh_token

router = APIRouter()


@router.post("/login/", response_model=TokenSchema)
async def login(
    request: Request,
    login_data: UserLoginSchema,
) -> TokenSchema:
    if not request.client:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="CITIZEN, YOUR CLIENT IS IN A STATE OF IRRATIONAL NON-EXISTENCE",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get client information
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")

    # Find user by email using repository
    user = await UserRepository.get_user_by_email(login_data.email)

    # Check if user exists and password is correct
    if not user or not await UserRepository.verify_user_password(
        user.id,
        login_data.password,
    ):
        # If user exists, record login failure
        if user:
            await UserRepository.record_login_failure(user.id, ip_address, user_agent)
            # Log the event
            await UserEventRepository.log_login_failure(user.id, ip_address, user_agent)
        else:
            # Log anonymous login failure
            await UserEventRepository.log_login_failure(None, ip_address, user_agent)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR CREDENTIALS REQUIRE CALIBRATION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="CITIZEN, YOUR ACCOUNT HAS BEEN LOCKED FOR RECALIBRATION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record successful login
    await UserRepository.record_login_success(user.id, ip_address, user_agent)

    # Log the event
    await UserEventRepository.log_login_success(user.id, ip_address, user_agent)

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
