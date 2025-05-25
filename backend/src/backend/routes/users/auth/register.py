from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from backend.db.models.user import User
from backend.routes.users.users_schemas import UserCreateSchema
from backend.routes.users.users_schemas import UserSchema

router = APIRouter()


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreateSchema) -> UserSchema:
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
