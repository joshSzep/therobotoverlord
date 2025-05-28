# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.auth.login import login
from backend.schemas.token import TokenSchema
from backend.schemas.user import UserLoginSchema


@pytest.mark.asyncio
async def test_login_success():
    """Test successful login."""
    # Arrange
    user_id = uuid.uuid4()
    email = "test@example.com"
    password = "test_password"

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.email = email
    mock_user.role = "user"
    mock_user.is_locked = False

    # Create mock request
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create login data
    login_data = UserLoginSchema(email=email, password=password)

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.auth.login.get_user_by_email",
            new=mock.AsyncMock(return_value=mock_user),
        ),
        mock.patch(
            "backend.routes.auth.login.verify_user_password",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.auth.login.record_login_success",
            new=mock.AsyncMock(),
        ) as mock_record_login_success,
        mock.patch(
            "backend.routes.auth.login.create_access_token",
            return_value="mock_access_token",
        ),
        mock.patch(
            "backend.routes.auth.login.create_refresh_token",
            return_value="mock_refresh_token",
        ),
    ):
        # Act
        result = await login(request=mock_request, login_data=login_data)

        # Assert
        assert isinstance(result, TokenSchema)
        assert result.access_token == "mock_access_token"
        assert result.refresh_token == "mock_refresh_token"
        assert result.token_type == "bearer"

        # Verify function calls
        mock_record_login_success.assert_called_once_with(
            user_id, "127.0.0.1", "Test User Agent"
        )


@pytest.mark.asyncio
async def test_login_invalid_password():
    """Test login with invalid password."""
    # Arrange
    user_id = uuid.uuid4()
    email = "test@example.com"
    password = "wrong_password"

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.email = email

    # Create mock request
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create login data
    login_data = UserLoginSchema(email=email, password=password)

    # Mock dependencies - simulate invalid password
    with (
        mock.patch(
            "backend.routes.auth.login.get_user_by_email",
            new=mock.AsyncMock(return_value=mock_user),
        ),
        mock.patch(
            "backend.routes.auth.login.verify_user_password",
            new=mock.AsyncMock(return_value=False),
        ),
        mock.patch(
            "backend.routes.auth.login.record_login_failure",
            new=mock.AsyncMock(),
        ) as mock_record_login_failure,
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await login(request=mock_request, login_data=login_data)

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "CREDENTIALS REQUIRE CALIBRATION" in excinfo.value.detail

        # Verify function calls
        mock_record_login_failure.assert_called_once_with(
            user_id, "127.0.0.1", "Test User Agent"
        )


@pytest.mark.asyncio
async def test_login_user_not_found():
    """Test login with non-existent user."""
    # Arrange
    email = "nonexistent@example.com"
    password = "test_password"

    # Create mock request
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create login data
    login_data = UserLoginSchema(email=email, password=password)

    # Mock dependencies - simulate user not found
    with (
        mock.patch(
            "backend.routes.auth.login.get_user_by_email",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.auth.login.record_login_failure",
            new=mock.AsyncMock(),
        ) as mock_record_login_failure,
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await login(request=mock_request, login_data=login_data)

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "CREDENTIALS REQUIRE CALIBRATION" in excinfo.value.detail

        # Verify function calls
        mock_record_login_failure.assert_called_once_with(
            None, "127.0.0.1", "Test User Agent"
        )


@pytest.mark.asyncio
async def test_login_locked_account():
    """Test login with a locked account."""
    # Arrange
    user_id = uuid.uuid4()
    email = "locked@example.com"
    password = "test_password"

    # Create mock user with locked account
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.email = email
    mock_user.is_locked = True

    # Create mock request
    mock_request = mock.MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {"User-Agent": "Test User Agent"}

    # Create login data
    login_data = UserLoginSchema(email=email, password=password)

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.auth.login.get_user_by_email",
            new=mock.AsyncMock(return_value=mock_user),
        ),
        mock.patch(
            "backend.routes.auth.login.verify_user_password",
            new=mock.AsyncMock(return_value=True),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await login(request=mock_request, login_data=login_data)

        # Verify the exception details
        assert excinfo.value.status_code == 410
        assert "ACCOUNT HAS BEEN LOCKED" in excinfo.value.detail


@pytest.mark.asyncio
async def test_login_missing_client():
    """Test login with missing client information."""
    # Arrange
    email = "test@example.com"
    password = "test_password"

    # Create mock request with no client
    mock_request = mock.MagicMock()
    mock_request.client = None

    # Create login data
    login_data = UserLoginSchema(email=email, password=password)

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await login(request=mock_request, login_data=login_data)

    # Verify the exception details
    assert excinfo.value.status_code == 417
    assert "CLIENT IS IN A STATE OF IRRATIONAL NON-EXISTENCE" in excinfo.value.detail
