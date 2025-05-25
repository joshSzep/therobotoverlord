from unittest import mock
import uuid

from fastapi import HTTPException
import pytest

from backend.routes.users.auth.register import register
from backend.routes.users.users_schemas import UserCreateSchema
from backend.routes.users.users_schemas import UserSchema


@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration."""
    # Arrange
    user_data = UserCreateSchema(
        email="new_user@example.com",
        display_name="New User",
        password="StrongP@ss123",
    )

    # Create a mock User instance
    mock_user = mock.AsyncMock()
    mock_user.id = str(uuid.uuid4())  # Generate a valid UUID
    mock_user.email = user_data.email
    mock_user.display_name = user_data.display_name
    mock_user.is_verified = False
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = "2025-05-25T00:00:00"
    mock_user.updated_at = "2025-05-25T00:00:00"
    mock_user.set_password = mock.AsyncMock()
    mock_user.save = mock.AsyncMock()

    # Mock dependencies to properly handle async
    with (
        mock.patch(
            "backend.routes.users.auth.register.User.get_or_none",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.utils.password.validate_password", return_value=(True, None)
        ),
        # Mock the User class itself - need a more complex setup
        mock.patch(
            "backend.routes.users.auth.register.User",
            **{
                "return_value": mock_user,
                # Ensure class methods are properly mocked as async
                "get_or_none": mock.AsyncMock(return_value=None),
            },
        ),
    ):
        # Act
        result = await register(user_data)

        # Assert
        assert isinstance(result, UserSchema)
        assert result.email == user_data.email
        assert result.display_name == user_data.display_name

        # Verify method calls
        mock_user.set_password.assert_called_once_with(user_data.password)
        mock_user.save.assert_called_once()


@pytest.mark.asyncio
async def test_register_email_already_exists():
    """Test registration with an email that already exists."""
    # Arrange
    user_data = UserCreateSchema(
        email="existing@example.com",
        display_name="Existing User",
        password="StrongP@ss123",
    )

    # Create a mock existing user
    mock_existing_user = mock.AsyncMock()

    # Mock dependencies - simulate existing user
    with mock.patch(
        "backend.routes.users.auth.register.User.get_or_none",
        new=mock.AsyncMock(return_value=mock_existing_user),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await register(user_data)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert "Email already registered" in excinfo.value.detail


@pytest.mark.asyncio
async def test_register_invalid_password():
    """
    Test registration with an invalid password.
    """
    # Arrange
    # Use a password that meets Pydantic's length validation but fails our custom reqs
    user_data = UserCreateSchema(
        email="new_user@example.com",
        display_name="New User",
        # Meets length requirement but will fail our validation
        password="weakpass",
    )

    error_message = "Password must contain at least one uppercase letter."

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.users.auth.register.User.get_or_none",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.utils.password.validate_password",
            return_value=(False, error_message),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await register(user_data)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert error_message in excinfo.value.detail


@pytest.mark.asyncio
async def test_register_db_integration():
    """Test user creation in database during registration."""
    # Arrange
    user_data = UserCreateSchema(
        email="test_db@example.com",
        display_name="DB Test User",
        password="StrongP@ss123",
    )

    # Create a real-like user instance that will be returned when User() is called
    mock_user = mock.AsyncMock()
    mock_user.id = str(uuid.uuid4())  # Generate a valid UUID
    mock_user.email = user_data.email
    mock_user.display_name = user_data.display_name
    mock_user.is_verified = False
    mock_user.last_login = None
    mock_user.role = "user"
    mock_user.created_at = "2025-05-25T00:00:00"
    mock_user.updated_at = "2025-05-25T00:00:00"
    mock_user.set_password = mock.AsyncMock()
    mock_user.save = mock.AsyncMock()

    # Mock the User creation but use a patch to check the constructor arguments
    with (
        mock.patch(
            "backend.routes.users.auth.register.User.get_or_none",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.utils.password.validate_password", return_value=(True, None)
        ),
        # Mock the User class itself with proper async methods
        mock.patch(
            "backend.routes.users.auth.register.User",
            **{
                "return_value": mock_user,
                # Ensure class methods are properly mocked as async
                "get_or_none": mock.AsyncMock(return_value=None),
            },
        ) as mock_user_class,
    ):
        # Act
        await register(user_data)

        # Assert
        # Check that User constructor was called with correct arguments
        mock_user_class.assert_called_once_with(
            email=user_data.email,
            display_name=user_data.display_name,
        )

        # Verify password was set and saved
        mock_user.set_password.assert_called_once_with(user_data.password)
        mock_user.save.assert_called_once()
