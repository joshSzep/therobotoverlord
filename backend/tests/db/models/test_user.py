"""Tests for the User model."""

from unittest import mock

import bcrypt
import pytest

from backend.db.models.login_attempt import LoginAttempt
from backend.db.models.user import User
from backend.db.models.user import UserRole
from backend.db.models.user_event import UserEvent
from backend.db.models.user_session import UserSession
from backend.utils.datetime import now_utc


@pytest.mark.asyncio
async def test_set_password() -> None:
    """Test setting a password correctly hashes it."""
    # Arrange
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    test_password = "SecureP@ssw0rd"

    # Act
    await user.set_password(test_password)

    # Assert
    assert user.password_hash is not None
    assert user.password_hash != test_password

    # Verify it's a valid bcrypt hash
    password_bytes = test_password.encode("utf-8")
    hash_bytes = user.password_hash.encode("utf-8")
    assert bcrypt.checkpw(password_bytes, hash_bytes)


@pytest.mark.asyncio
async def test_verify_password_correct() -> None:
    """Test verifying a correct password."""
    # Arrange
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    test_password = "SecureP@ssw0rd"
    await user.set_password(test_password)

    # Act
    result = await user.verify_password(test_password)

    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_verify_password_incorrect() -> None:
    """Test verifying an incorrect password."""
    # Arrange
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    test_password = "SecureP@ssw0rd"
    await user.set_password(test_password)

    # Act
    result = await user.verify_password("WrongP@ssw0rd")

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_record_login_success() -> None:
    """Test recording a successful login."""
    # Arrange
    user = mock.AsyncMock()
    user.last_login = None
    user.failed_login_attempts = 2
    user.is_locked = True

    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"

    # Mock imported methods
    with (
        mock.patch("backend.db.models.user.now_utc", return_value=now_utc()),
        # Mock secrets module within the function's import scope
        mock.patch("secrets.token_hex", return_value="mock_token"),
        mock.patch.object(UserSession, "create", new=mock.AsyncMock()),
        mock.patch.object(LoginAttempt, "create", new=mock.AsyncMock()),
    ):
        # Act
        await User.record_login_success(user, ip_address, user_agent)

        # Assert
        # Verify user fields were updated correctly
        assert user.last_login is not None
        assert user.failed_login_attempts == 0
        assert user.is_locked is False
        user.save.assert_called_once()

        # Verify session was created
        UserSession.create.assert_called_once_with(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            session_token="mock_token",
            is_active=True,
            expires_at=mock.ANY,
        )

        # Verify login attempt was recorded
        LoginAttempt.create.assert_called_once_with(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )


@pytest.mark.asyncio
async def test_record_login_failure_without_locking() -> None:
    """Test recording a failed login without locking the account."""
    # Arrange
    user = mock.AsyncMock()
    user.failed_login_attempts = 2  # This will be incremented to 3, not enough to lock
    user.is_locked = False

    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"

    # Mock imported methods
    with mock.patch.object(LoginAttempt, "create", new=mock.AsyncMock()):
        # Act
        await User.record_login_failure(user, ip_address, user_agent)

        # Assert
        # Verify user fields were updated correctly
        assert user.failed_login_attempts == 3
        assert user.is_locked is False
        user.save.assert_called_once()

        # Verify login attempt was recorded
        LoginAttempt.create.assert_called_once_with(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
        )


@pytest.mark.asyncio
async def test_record_login_failure_with_locking() -> None:
    """Test recording a failed login that locks the account."""
    # Arrange
    user = mock.AsyncMock()
    user.failed_login_attempts = 4  # This will be incremented to 5, enough to lock
    user.is_locked = False
    user.id = "test-user-id"

    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"

    # Mock imported methods
    with (
        mock.patch.object(LoginAttempt, "create", new=mock.AsyncMock()),
        mock.patch.object(UserEvent, "log_account_lockout", new=mock.AsyncMock()),
    ):
        # Act
        await User.record_login_failure(user, ip_address, user_agent)

        # Assert
        # Verify user fields were updated correctly
        assert user.failed_login_attempts == 5
        assert user.is_locked is True
        user.save.assert_called_once()

        # Verify login attempt was recorded
        LoginAttempt.create.assert_called_once_with(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
        )

        # Verify lockout event was logged
        UserEvent.log_account_lockout.assert_called_once_with(
            user.id, ip_address, user_agent
        )


@pytest.mark.asyncio
async def test_user_role_enum() -> None:
    """Test the UserRole enum values."""
    # Arrange & Act & Assert
    assert UserRole.USER == "user"
    assert UserRole.MODERATOR == "moderator"
    assert UserRole.ADMIN == "admin"


@pytest.mark.asyncio
async def test_create_user() -> None:
    """Test creating a user with default values."""
    # Arrange
    email = "test@example.com"
    display_name = "Test User"

    # Mock the User.create method
    with mock.patch.object(User, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await User.create(email=email, display_name=display_name)

        # Assert
        mock_create.assert_called_once_with(
            email=email,
            display_name=display_name,
        )
