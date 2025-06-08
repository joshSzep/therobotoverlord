from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from backend.db_functions.users.create_admin_user import create_admin_user
from backend.db_functions.users.get_user_by_email import get_user_by_email
from backend.schemas.admin import AdminUserCreate
from backend.schemas.user import UserSchema
from backend.utils.password import validate_password
from backend.utils.settings import settings

router = APIRouter()


@router.post(
    "/create-admin/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_admin_user_route(admin_data: AdminUserCreate) -> UserSchema:
    """
    Create a new admin user. Requires the correct JWT secret key.
    """
    # Verify the secret key matches the JWT secret
    if admin_data.secret_key != settings.JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CITIZEN, YOUR SECRET KEY HAS FAILED VERIFICATION",
        )

    # Check if email already exists
    existing_user = await get_user_by_email(admin_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate password
    is_valid, error_message = validate_password(admin_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    # Create new admin user
    user = await create_admin_user(
        email=admin_data.email,
        password=admin_data.password,
        display_name=admin_data.display_name,
    )

    # Return user data (without password)
    return UserSchema(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_verified=user.is_verified,
        last_login=user.last_login,
        role=user.role,
        is_locked=user.is_locked,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
