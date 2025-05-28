# Standard library imports

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

# Project-specific imports
from backend.db_functions.users import create_user
from backend.db_functions.users import get_user_by_email
from backend.schemas.user import UserCreateSchema
from backend.schemas.user import UserSchema
from backend.utils.password import validate_password

router = APIRouter()


@router.post(
    "/register/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreateSchema) -> UserSchema:
    # Check if email already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    is_valid, error_message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    # Create new user using data access function
    user = await create_user(
        email=user_data.email,
        password=user_data.password,
        display_name=user_data.display_name,
    )

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
