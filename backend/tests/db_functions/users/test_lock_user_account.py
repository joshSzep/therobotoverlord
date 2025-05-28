# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.users.lock_user_account import lock_user_account
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.is_verified = True
    user.last_login = mock.MagicMock()
    user.failed_login_attempts = 3
    user.is_locked = False
    user.role = "user"
    user.created_at = mock.MagicMock()
    user.updated_at = mock.MagicMock()
    user.save = mock.AsyncMock()
    return user


@pytest.fixture
def mock_user_schema(mock_user) -> UserSchema:
    return UserSchema(
        id=mock_user.id,
        email=mock_user.email,
        display_name=mock_user.display_name,
        is_verified=mock_user.is_verified,
        role=mock_user.role,
        is_locked=True,  # Should be updated after locking
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
        last_login=mock_user.last_login,
    )


@pytest.mark.asyncio
async def test_lock_user_account_success(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.lock_user_account.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
    ):
        # Act
        result = await lock_user_account(test_id)

        # Assert
        assert result is not None
        assert result.id == mock_user.id
        assert result.is_locked is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.is_locked is True
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_lock_user_account_user_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await lock_user_account(test_id)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_lock_user_account_already_locked(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id
    mock_user.is_locked = True  # User is already locked

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.lock_user_account.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
    ):
        # Act
        result = await lock_user_account(test_id)

        # Assert
        assert result is not None
        assert result.is_locked is True

        # Verify function calls - should still save even if already locked
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.is_locked is True
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_lock_user_account_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = OperationalError("Database error")

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await lock_user_account(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_lock_user_account_save_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    save_error = IntegrityError("Error saving user")
    mock_user.save.side_effect = save_error

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await lock_user_account(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()


@pytest.mark.asyncio
async def test_lock_user_account_converter_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.lock_user_account.user_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await lock_user_account(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)
