from unittest import mock

from fastapi import HTTPException
import pytest

from backend.db.models.user import User
from backend.db.models.user_event import UserEvent
from backend.routes.users.auth.login import login
from backend.routes.users.users_schemas import TokenSchema
from backend.routes.users.users_schemas import UserLoginSchema


@pytest.mark.asyncio
async def test_login_success():
    # Arrange
    login_data = UserLoginSchema(
        email="test@example.com",
        password="Password123!",
    )

    # Mock the request object
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test Browser"}

    # Create a mock user
    mock_user = mock.AsyncMock()
    mock_user.id = "test-user-id"
    mock_user.email = "test@example.com"
    mock_user.role = "user"
    mock_user.is_locked = False
    mock_user.verify_password = mock.AsyncMock(return_value=True)

    # Mock User.get_or_none to return our mock user
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ),
        mock.patch.object(
            UserEvent, "log_login_success", new=mock.AsyncMock(return_value=None)
        ),
        mock.patch(
            "backend.routes.users.auth.login.create_access_token",
            return_value="mock_access_token",
        ),
        mock.patch(
            "backend.routes.users.auth.login.create_refresh_token",
            return_value="mock_refresh_token",
        ),
    ):
        # Act
        result = await login(mock_request, login_data)

        # Assert
        assert isinstance(result, TokenSchema)
        assert result.access_token == "mock_access_token"
        assert result.refresh_token == "mock_refresh_token"
        assert result.token_type == "bearer"

        # Verify mock calls
        mock_user.verify_password.assert_called_once_with("Password123!")
        mock_user.record_login_success.assert_called_once_with(
            "127.0.0.1", "Test Browser"
        )


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    # Arrange
    login_data = UserLoginSchema(
        email="test@example.com",
        password="WrongPassword",
    )

    # Mock the request object
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test Browser"}

    # Create a mock user
    mock_user = mock.AsyncMock()
    mock_user.id = "test-user-id"
    mock_user.verify_password = mock.AsyncMock(return_value=False)

    # Mock User.get_or_none to return our mock user
    with (
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ),
        mock.patch.object(
            UserEvent, "log_login_failure", new=mock.AsyncMock(return_value=None)
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await login(mock_request, login_data)

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "CREDENTIALS REQUIRE CALIBRATION" in excinfo.value.detail

        # Verify mock calls
        mock_user.verify_password.assert_called_once_with("WrongPassword")
        mock_user.record_login_failure.assert_called_once_with(
            "127.0.0.1", "Test Browser"
        )


@pytest.mark.asyncio
async def test_login_user_not_found():
    """Test login with non-existent user."""
    # Arrange
    login_data = UserLoginSchema(
        email="nonexistent@example.com",
        password="Password123!",
    )

    # Mock the request object
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test Browser"}

    # Mock User.get_or_none to return None (user not found)
    with (
        mock.patch.object(User, "get_or_none", new=mock.AsyncMock(return_value=None)),
        mock.patch.object(
            UserEvent, "log_login_failure", new=mock.AsyncMock(return_value=None)
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await login(mock_request, login_data)

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "CREDENTIALS REQUIRE CALIBRATION" in excinfo.value.detail

        # Verify mock calls
        UserEvent.log_login_failure.assert_called_once_with(  # type: ignore
            None, "127.0.0.1", "Test Browser"
        )


@pytest.mark.asyncio
async def test_login_account_locked():
    # Arrange
    login_data = UserLoginSchema(
        email="locked@example.com",
        password="Password123!",
    )

    # Mock the request object
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test Browser"}

    # Create a mock user with is_locked=True
    mock_user = mock.AsyncMock()
    mock_user.id = "locked-user-id"
    mock_user.verify_password = mock.AsyncMock(return_value=True)
    mock_user.is_locked = True

    # Mock User.get_or_none to return our locked mock user
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await login(mock_request, login_data)

        # Verify the exception details
        assert excinfo.value.status_code == 410
        assert "ACCOUNT HAS BEEN LOCKED" in excinfo.value.detail

        # Verify mock calls
        mock_user.verify_password.assert_called_once_with("Password123!")


@pytest.mark.asyncio
async def test_login_missing_client():
    # Arrange
    login_data = UserLoginSchema(
        email="test@example.com",
        password="Password123!",
    )

    # Mock the request object with client=None
    mock_request = mock.MagicMock()
    mock_request.client = None

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await login(mock_request, login_data)

    # Verify the exception details
    assert excinfo.value.status_code == 417
    assert "CLIENT IS IN A STATE OF IRRATIONAL NON-EXISTENCE" in excinfo.value.detail
