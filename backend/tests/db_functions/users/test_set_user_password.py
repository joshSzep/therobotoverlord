# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

from backend.db.models.user import User

# Project-specific imports
from backend.db_functions.users.set_user_password import set_user_password
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
        is_locked=mock_user.is_locked,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
        last_login=mock_user.last_login,
    )


@pytest.mark.asyncio
async def test_set_user_password_success(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id
    test_password = "new_password123"

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.set_user_password.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.users.set_user_password.bcrypt.gensalt",
            return_value=b"mock_salt",
        ) as mock_gensalt,
        mock.patch(
            "backend.db_functions.users.set_user_password.bcrypt.hashpw",
            return_value=b"hashed_password",
        ) as mock_hashpw,
    ):
        # Act
        result = await set_user_password(test_id, test_password)

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
        mock_get.assert_called_once_with(id=test_id)
        mock_gensalt.assert_called_once()
        mock_hashpw.assert_called_once_with(test_password.encode("utf-8"), b"mock_salt")
        assert mock_user.password_hash == "hashed_password"
        mock_user.save.assert_called_once()
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_set_user_password_user_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_password = "new_password123"

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await set_user_password(test_id, test_password)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_set_user_password_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_password = "new_password123"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await set_user_password(test_id, test_password)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_set_user_password_bcrypt_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_password = "new_password123"
    bcrypt_error = ValueError("Bcrypt hashing error")

    # Mock the database query and bcrypt functions
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.set_user_password.bcrypt.gensalt",
            side_effect=bcrypt_error,
        ) as mock_gensalt,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await set_user_password(test_id, test_password)

        # Verify the exception is propagated correctly
        assert exc_info.value == bcrypt_error
        mock_get.assert_called_once_with(id=test_id)
        mock_gensalt.assert_called_once()


@pytest.mark.asyncio
async def test_set_user_password_save_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_password = "new_password123"
    save_error = IntegrityError("Error saving user")
    mock_user.save.side_effect = save_error

    # Mock the database query and bcrypt functions
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.set_user_password.bcrypt.gensalt",
            return_value=b"mock_salt",
        ) as mock_gensalt,
        mock.patch(
            "backend.db_functions.users.set_user_password.bcrypt.hashpw",
            return_value=b"hashed_password",
        ) as mock_hashpw,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await set_user_password(test_id, test_password)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_gensalt.assert_called_once()
        mock_hashpw.assert_called_once_with(test_password.encode("utf-8"), b"mock_salt")
        assert mock_user.password_hash == "hashed_password"
        mock_user.save.assert_called_once()
