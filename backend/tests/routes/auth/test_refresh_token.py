from unittest import mock

from fastapi import HTTPException
import jwt
import pytest

from backend.db.models.user import User
from backend.routes.auth.refresh_token import refresh_token
from backend.schemas.token import TokenSchema
from backend.utils.settings import settings


@pytest.mark.asyncio
async def test_refresh_token_success():
    """Test successful token refresh."""
    # Arrange
    # Create a valid refresh token payload
    user_id = "test-user-id"
    payload = {
        "sub": user_id,
        "refresh": True,
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Mock the request object
    mock_request = mock.MagicMock()

    # Create a mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.role = "user"
    mock_user.is_locked = False

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.auth.refresh_token.decode_token", return_value=payload
        ),
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ),
        mock.patch(
            "backend.routes.auth.refresh_token.create_access_token",
            return_value="new_access_token",
        ),
        mock.patch(
            "backend.routes.auth.refresh_token.create_refresh_token",
            return_value="new_refresh_token",
        ),
    ):
        # Act
        result = await refresh_token(mock_request, token)

        # Assert
        assert isinstance(result, TokenSchema)
        assert result.access_token == "new_access_token"
        assert result.refresh_token == "new_refresh_token"
        assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_not_refresh_token():
    """Test using an access token as a refresh token."""
    # Arrange
    # Create a token without the refresh flag
    payload = {
        "sub": "test-user-id",
        # No refresh flag
    }

    # Mock the request object
    mock_request = mock.MagicMock()

    # Mock dependencies
    with mock.patch(
        "backend.routes.auth.refresh_token.decode_token", return_value=payload
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await refresh_token(mock_request, "fake_token")

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "Invalid refresh token" in excinfo.value.detail


@pytest.mark.asyncio
async def test_refresh_token_missing_user_id():
    """Test refresh token without a user ID."""
    # Arrange
    # Create a token without a user ID
    payload = {
        "refresh": True,
        # No user ID
    }

    # Mock the request object
    mock_request = mock.MagicMock()

    # Mock dependencies
    with mock.patch(
        "backend.routes.auth.refresh_token.decode_token", return_value=payload
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await refresh_token(mock_request, "fake_token")

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "Invalid refresh token" in excinfo.value.detail


@pytest.mark.asyncio
async def test_refresh_token_user_not_found():
    """Test refresh token with non-existent user."""
    # Arrange
    payload = {
        "sub": "nonexistent-user-id",
        "refresh": True,
    }

    # Mock the request object
    mock_request = mock.MagicMock()

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.auth.refresh_token.decode_token", return_value=payload
        ),
        mock.patch.object(User, "get_or_none", new=mock.AsyncMock(return_value=None)),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await refresh_token(mock_request, "fake_token")

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "User not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_refresh_token_locked_account():
    """Test refresh token with a locked account."""
    # Arrange
    user_id = "locked-user-id"
    payload = {
        "sub": user_id,
        "refresh": True,
    }

    # Mock the request object
    mock_request = mock.MagicMock()

    # Create a mock user with is_locked=True
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.is_locked = True

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.auth.refresh_token.decode_token", return_value=payload
        ),
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await refresh_token(mock_request, "fake_token")

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "Account is locked" in excinfo.value.detail


@pytest.mark.asyncio
async def test_refresh_token_invalid_token():
    """
    Test refresh with an invalid token that raises an exception during verification.
    """
    # Arrange
    # Mock the request object
    mock_request = mock.MagicMock()

    # Mock decode_token to raise an exception
    with mock.patch(
        "backend.routes.auth.refresh_token.decode_token",
        side_effect=Exception("Invalid token"),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await refresh_token(mock_request, "invalid_token")

        # Verify the exception details
        assert excinfo.value.status_code == 401
        assert "Invalid refresh token" in excinfo.value.detail
