# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

from backend.db.models.user import User

# Project-specific imports
from backend.db_functions.users.record_login_failure import record_login_failure
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
        is_locked=mock_user.is_locked,
        created_at=mock_user.created_at,
        updated_at=mock_user.updated_at,
        last_login=mock_user.last_login,
    )


@pytest.mark.asyncio
async def test_record_login_failure_with_user_found(
    mock_user, mock_user_schema
) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_failure.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(),
        ) as mock_log_failure,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_account_lockout",
            new=mock.AsyncMock(),
        ) as mock_log_lockout,
    ):
        # Act
        result = await record_login_failure(test_id, test_ip, test_user_agent)

        # Assert
        assert result is not None
        assert result.id == mock_user.id

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.failed_login_attempts == 4  # Incremented from 3 to 4
        assert (
            mock_user.is_locked is False
        )  # Should still be False (not yet 5 attempts)
        mock_user.save.assert_called_once()
        mock_log_failure.assert_called_once_with(
            user_id=test_id, ip_address=test_ip, user_agent=test_user_agent
        )
        mock_log_lockout.assert_not_called()  # Account not locked yet
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_record_login_failure_with_account_lockout(
    mock_user, mock_user_schema
) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    mock_user.failed_login_attempts = 4  # One more failure will trigger lockout

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_failure.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(),
        ) as mock_log_failure,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_account_lockout",
            new=mock.AsyncMock(),
        ) as mock_log_lockout,
    ):
        # Act
        result = await record_login_failure(test_id, test_ip, test_user_agent)

        # Assert
        assert result is not None
        assert result.id == mock_user.id

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.failed_login_attempts == 5  # Incremented from 4 to 5
        assert mock_user.is_locked is True  # Should be locked now (5 attempts)
        mock_user.save.assert_called_once()
        mock_log_failure.assert_called_once_with(
            user_id=test_id, ip_address=test_ip, user_agent=test_user_agent
        )
        mock_log_lockout.assert_called_once_with(test_id, test_ip, test_user_agent)
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_record_login_failure_with_already_locked_account(
    mock_user, mock_user_schema
) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    mock_user.failed_login_attempts = 5  # Already at threshold
    mock_user.is_locked = True  # Already locked

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_failure.user_to_schema",
            new=mock.AsyncMock(return_value=mock_user_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(),
        ) as mock_log_failure,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_account_lockout",
            new=mock.AsyncMock(),
        ) as mock_log_lockout,
    ):
        # Act
        result = await record_login_failure(test_id, test_ip, test_user_agent)

        # Assert
        assert result is not None
        assert result.id == mock_user.id

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.failed_login_attempts == 6  # Incremented from 5 to 6
        assert mock_user.is_locked is True  # Still locked
        mock_user.save.assert_called_once()
        mock_log_failure.assert_called_once_with(
            user_id=test_id, ip_address=test_ip, user_agent=test_user_agent
        )
        mock_log_lockout.assert_not_called()  # Account was already locked
        mock_converter.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_record_login_failure_user_id_none() -> None:
    # Arrange
    test_id = None
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"

    # Mock the log_login_failure function
    with mock.patch(
        "backend.db_functions.users.record_login_failure.log_login_failure",
        new=mock.AsyncMock(),
    ) as mock_log_failure:
        # Act
        result = await record_login_failure(test_id, test_ip, test_user_agent)

        # Assert
        assert result is None
        mock_log_failure.assert_called_once_with(None, test_ip, test_user_agent)


@pytest.mark.asyncio
async def test_record_login_failure_user_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=None)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(),
        ) as mock_log_failure,
    ):
        # Act
        result = await record_login_failure(test_id, test_ip, test_user_agent)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)
        mock_log_failure.assert_called_once_with(None, test_ip, test_user_agent)


@pytest.mark.asyncio
async def test_record_login_failure_database_error() -> None:
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
            await record_login_failure(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_record_login_failure_save_error(mock_user) -> None:
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
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(),
        ) as mock_log_failure,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await record_login_failure(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()
        mock_log_failure.assert_not_called()  # Should not be called if save fails


@pytest.mark.asyncio
async def test_record_login_failure_log_failure_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    log_error = ValueError("Error logging failure")

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(side_effect=log_error),
        ) as mock_log_failure,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await record_login_failure(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == log_error
        mock_get.assert_called_once_with(id=test_id)
        mock_user.save.assert_called_once()
        mock_log_failure.assert_called_once_with(
            user_id=test_id, ip_address=test_ip, user_agent=test_user_agent
        )


@pytest.mark.asyncio
async def test_record_login_failure_log_lockout_error(mock_user) -> None:
    # Arrange
    test_id = mock_user.id
    test_ip = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    mock_user.failed_login_attempts = 4  # One more failure will trigger lockout
    log_error = ValueError("Error logging lockout")

    # Mock the database query
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_login_failure",
            new=mock.AsyncMock(),
        ) as mock_log_failure,
        mock.patch(
            "backend.db_functions.users.record_login_failure.log_account_lockout",
            new=mock.AsyncMock(side_effect=log_error),
        ) as mock_log_lockout,
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await record_login_failure(test_id, test_ip, test_user_agent)

        # Verify the exception is propagated correctly
        assert exc_info.value == log_error
        mock_get.assert_called_once_with(id=test_id)
        assert mock_user.failed_login_attempts == 5  # Incremented from 4 to 5
        assert mock_user.is_locked is True  # Should be locked now (5 attempts)
        mock_user.save.assert_called_once()
        mock_log_failure.assert_called_once_with(
            user_id=test_id, ip_address=test_ip, user_agent=test_user_agent
        )
        mock_log_lockout.assert_called_once_with(test_id, test_ip, test_user_agent)
