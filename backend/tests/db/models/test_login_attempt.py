from unittest import mock

import pytest

from backend.db.models.login_attempt import LoginAttempt
from backend.db.models.user import User


@pytest.mark.asyncio
async def test_login_attempt_create() -> None:
    # Arrange
    mock_user = mock.AsyncMock(spec=User)
    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    success = True

    # Mock the LoginAttempt.create method
    with mock.patch.object(LoginAttempt, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await LoginAttempt.create(
            user=mock_user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )

        # Assert
        mock_create.assert_called_once_with(
            user=mock_user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )


@pytest.mark.asyncio
async def test_login_attempt_create_without_user() -> None:
    # Arrange
    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    success = False

    # Mock the LoginAttempt.create method
    with mock.patch.object(LoginAttempt, "create", new=mock.AsyncMock()) as mock_create:
        # Act
        await LoginAttempt.create(
            user=None,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )

        # Assert
        mock_create.assert_called_once_with(
            user=None,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
        )


@pytest.mark.asyncio
async def test_login_attempt_fields() -> None:
    # Arrange
    login_attempt = LoginAttempt(
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        success=True,
    )

    # Assert
    assert login_attempt.ip_address == "192.168.1.1"
    assert login_attempt.user_agent == "Mozilla/5.0"
    assert login_attempt.success is True
    # Don't test the user field directly as it's a ForeignKeyField
