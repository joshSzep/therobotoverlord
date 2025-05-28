# Standard library imports
from unittest import mock
import uuid

import bcrypt

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

from backend.db.models.user import User

# Project-specific imports
from backend.db_functions.users.verify_user_password import verify_user_password


@pytest.fixture
def create_password_hash(password="correct_password"):
    """Create a bcrypt hash for testing."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


@pytest.fixture
def mock_user(create_password_hash) -> mock.MagicMock:
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.password_hash = create_password_hash
    return user


@pytest.mark.asyncio
async def test_verify_user_password_correct(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_password = "correct_password"

    # Mock the database query - RULE #10 compliance: only operates on User model
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
    ) as mock_get:
        # Act
        result = await verify_user_password(test_id, test_password)

        # Assert
        assert result is True
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_verify_user_password_incorrect(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_password = "wrong_password"

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
    ) as mock_get:
        # Act
        result = await verify_user_password(test_id, test_password)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_verify_user_password_user_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_password = "any_password"

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await verify_user_password(test_id, test_password)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_verify_user_password_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_password = "any_password"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await verify_user_password(test_id, test_password)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_verify_user_password_bcrypt_exception() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_password = "any_password"

    # Create a user with invalid hash format
    invalid_user = mock.MagicMock(spec=User)
    invalid_user.id = test_id
    invalid_user.password_hash = "invalid_hash_format"

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=invalid_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.verify_user_password.bcrypt.checkpw",
            new=mock.MagicMock(side_effect=ValueError("Invalid salt")),
        ) as mock_checkpw,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await verify_user_password(test_id, test_password)

        # Verify the function calls and exception
        assert str(exc_info.value) == "Invalid salt"
        mock_get.assert_called_once_with(id=test_id)
        mock_checkpw.assert_called_once()
