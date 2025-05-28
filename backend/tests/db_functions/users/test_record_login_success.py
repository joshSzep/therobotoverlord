# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

from backend.db.models.user import User

# Project-specific imports
from backend.db_functions.users.record_login_success import record_login_success
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.is_verified = False
    user.last_login = None
    user.failed_login_attempts = 3
    user.is_locked = True
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
        is_locked=False,  # Should be updated after successful login
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
        last_login=datetime.now(),  # Should be updated after successful login
    )


@pytest.mark.asyncio
async def test_record_login_success(mock_user, mock_user_schema) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    mock_now = datetime.now()

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_success.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.users.record_login_success.create_session",
            new=mock.AsyncMock(return_value=mock.MagicMock()),
        ) as mock_create_session,
        mock.patch(
            "backend.db_functions.users.record_login_success.log_login_success",
            new=mock.AsyncMock(return_value=mock.MagicMock()),
        ) as mock_log_login,
        mock.patch(
            "backend.db_functions.users.record_login_success.now_utc",
            return_value=mock_now,
        ) as mock_now_utc,
    ):
        # Act
        result = await record_login_success(test_id, test_ip, test_user_agent)

        # Assert
        assert result is not None
        assert result.id == mock_user.id
        # Skip datetime comparisons as they may cause issues with mock objects

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_now_utc.assert_called_once()
        assert mock_user.last_login == mock_now
        assert mock_user.failed_login_attempts == 0
        assert mock_user.is_locked is False
        mock_user.save.assert_called_once()

        # Verify delegated function calls
        mock_create_session.assert_called_once_with(
            user_id=test_id,
            ip_address=test_ip,
            user_agent=test_user_agent,
        )
        mock_log_login.assert_called_once_with(test_id, test_ip, test_user_agent)
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_record_login_success_user_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"

    # Mock the database query
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await record_login_success(test_id, test_ip, test_user_agent)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_record_login_success_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await record_login_success(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_record_login_success_save_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    save_error = IntegrityError("Error saving user")
    mock_user.save.side_effect = save_error

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_success.now_utc",
            return_value=datetime.now(),
        ),
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await record_login_success(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()


@pytest.mark.asyncio
async def test_record_login_success_create_session_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    session_error = ValueError("Error creating session")

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_success.now_utc",
            return_value=datetime.now(),
        ),
        mock.patch(
            "backend.db_functions.users.record_login_success.create_session",
            new=mock.AsyncMock(side_effect=session_error),
        ) as mock_create_session,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await record_login_success(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == session_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()
        mock_create_session.assert_called_once_with(
            user_id=test_id,
            ip_address=test_ip,
            user_agent=test_user_agent,
        )


@pytest.mark.asyncio
async def test_record_login_success_log_event_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    log_error = ValueError("Error logging event")

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_success.now_utc",
            return_value=datetime.now(),
        ),
        mock.patch(
            "backend.db_functions.users.record_login_success.create_session",
            new=mock.AsyncMock(return_value=mock.MagicMock()),
        ) as mock_create_session,
        mock.patch(
            "backend.db_functions.users.record_login_success.log_login_success",
            new=mock.AsyncMock(side_effect=log_error),
        ) as mock_log_login,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await record_login_success(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == log_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()
        mock_create_session.assert_called_once_with(
            user_id=test_id,
            ip_address=test_ip,
            user_agent=test_user_agent,
        )
        mock_log_login.assert_called_once_with(test_id, test_ip, test_user_agent)
