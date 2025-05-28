# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

from backend.db.models.user import User

# Project-specific imports
from backend.db_functions.users.create_user import create_user
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.password_hash = ""
    user.is_verified = False
    user.last_login = None
    user.role = "user"
    user.is_locked = False
    user.created_at = mock.MagicMock()
    user.updated_at = mock.MagicMock()
    return user


@pytest.fixture
def mock_user_schema(mock_user) -> UserSchema:
    return UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name=mock_user.display_name,
        is_verified=mock_user.is_verified,
        role=mock_user.role,
        is_locked=mock_user.is_locked,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
        last_login=mock_user.last_login,
    )


@pytest.mark.asyncio
async def test_create_user_success(mock_user, mock_user_schema) -> None:
    # Arrange
    test_email = "test@example.com"
    test_password = "password123"
    test_display_name = "Test User"

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(
            User, "create", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.users.create_user.set_user_password",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_set_password,
    ):
        # Act
        result = await create_user(
            email=test_email, password=test_password, display_name=test_display_name
        )

        # Assert
        assert result is not None
        assert result.id == mock_user.id
        assert result.email == mock_user.email
        assert result.display_name == mock_user.display_name
        assert result.is_verified == mock_user.is_verified
        assert result.role == mock_user.role
        assert result.is_locked == mock_user.is_locked
        # Skip datetime comparisons as they may cause issues with mock objects

        # Verify function calls
        mock_create.assert_called_once_with(
            email=test_email,
            password_hash="",  # Temporary placeholder
            display_name=test_display_name,
        )
        mock_set_password.assert_called_once_with(mock_user.id, test_password)


@pytest.mark.asyncio
async def test_create_user_duplicate_email() -> None:
    # Arrange
    test_email = "existing@example.com"
    test_password = "password123"
    test_display_name = "Existing User"
    db_error = IntegrityError("User with this email already exists")

    # Mock the database query to raise an exception
    with mock.patch.object(
        User, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_user(
                email=test_email, password=test_password, display_name=test_display_name
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(
            email=test_email, password_hash="", display_name=test_display_name
        )


@pytest.mark.asyncio
async def test_create_user_password_hashing(mock_user) -> None:
    # Arrange
    test_email = "test@example.com"
    test_password = "password123"
    test_display_name = "Test User"

    # Mock the database query and set_user_password
    with (
        mock.patch.object(
            User, "create", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.users.create_user.set_user_password",
            new=mock.AsyncMock(return_value=None),  # Simulate failure
        ) as mock_set_password,
    ):
        # Act & Assert
        with pytest.raises(
            ValueError, match=f"Failed to set password for user {mock_user.id}"
        ):
            await create_user(
                email=test_email, password=test_password, display_name=test_display_name
            )

        # Verify function calls
        mock_create.assert_called_once_with(
            email=test_email, password_hash="", display_name=test_display_name
        )
        mock_set_password.assert_called_once_with(mock_user.id, test_password)


@pytest.mark.asyncio
async def test_create_user_set_password_error(mock_user) -> None:
    # Arrange
    test_email = "test@example.com"
    test_password = "password123"
    test_display_name = "Test User"
    password_error = ValueError("Password hashing failed")

    # Mock the database query and set_user_password
    with (
        mock.patch.object(
            User, "create", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.users.create_user.set_user_password",
            new=mock.AsyncMock(side_effect=password_error),
        ) as mock_set_password,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await create_user(
                email=test_email, password=test_password, display_name=test_display_name
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == password_error
        mock_create.assert_called_once_with(
            email=test_email, password_hash="", display_name=test_display_name
        )
        mock_set_password.assert_called_once_with(mock_user.id, test_password)
