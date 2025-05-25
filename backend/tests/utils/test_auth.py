"""Tests for authentication utilities."""

from datetime import timedelta
import time
from typing import Union
from unittest import mock

from fastapi import HTTPException
import jwt
import pytest

from backend.db.models.user import User
from backend.utils.auth import create_access_token
from backend.utils.auth import create_refresh_token
from backend.utils.auth import get_current_user
from backend.utils.auth import get_optional_user
from backend.utils.auth import verify_token
from backend.utils.settings import settings


@pytest.mark.asyncio
async def test_create_access_token() -> None:
    """Test creating an access token."""
    # Arrange
    test_data = {"sub": "test-user-id"}

    # Act
    token = create_access_token(data=test_data)

    # Assert
    assert token is not None
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == "test-user-id"
    assert "exp" in payload

    # Test with custom expiration
    custom_expires = timedelta(minutes=5)
    token_with_expiration = create_access_token(
        data=test_data, expires_delta=custom_expires
    )
    payload = jwt.decode(
        token_with_expiration,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    # Ensure expiration is within expected range (allowing 1 second for execution time)
    expected_exp = int(time.time()) + int(custom_expires.total_seconds())
    assert abs(payload["exp"] - expected_exp) <= 1


@pytest.mark.asyncio
async def test_create_refresh_token() -> None:
    """Test creating a refresh token."""
    # Arrange
    test_data = {"sub": "test-user-id"}

    # Act
    token = create_refresh_token(data=test_data)

    # Assert
    assert token is not None
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == "test-user-id"
    assert payload["refresh"] is True
    assert "exp" in payload

    # Ensure expiration is set correctly
    # Ensure expiration is within a reasonable range (24 hours in seconds)
    seconds_per_day = 24 * 60 * 60
    days_in_seconds = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * seconds_per_day
    expected_exp_approx = int(time.time()) + days_in_seconds
    assert abs(payload["exp"] - expected_exp_approx) <= seconds_per_day


@pytest.mark.asyncio
async def test_verify_token_valid() -> None:
    """Test verifying a valid token."""
    # Arrange
    test_data = {"sub": "test-user-id"}
    token = create_access_token(data=test_data)

    # Act
    payload = verify_token(token)

    # Assert
    assert payload["sub"] == "test-user-id"


@pytest.mark.asyncio
async def test_verify_token_expired() -> None:
    """Test verifying an expired token."""
    # Arrange - Create our own expired token for this test
    payload: dict[str, Union[str, int]] = {"sub": "test-user-id"}
    expire = int(time.time()) - 3600  # 1 hour in the past
    payload["exp"] = expire
    expired_token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        verify_token(expired_token)

    assert excinfo.value.status_code == 401
    assert "AUTHENTICATION TOKEN HAS FAILED INSPECTION" in excinfo.value.detail


@pytest.mark.asyncio
async def test_verify_token_invalid(invalid_token: str) -> None:
    """Test verifying an invalid token."""
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        verify_token(invalid_token)

    assert excinfo.value.status_code == 401
    assert "AUTHENTICATION TOKEN HAS FAILED INSPECTION" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_current_user() -> None:
    """Test getting the current user from a valid token."""
    # Arrange
    user_id = "test-user-id"
    token = create_access_token(data={"sub": user_id})

    # Create a mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.is_locked = False

    # Mock User.get_or_none to return our mock user
    with mock.patch.object(
        User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
    ):
        # Act
        user = await get_current_user(token)

        # Assert
        assert user is not None
        assert user.id == user_id


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(invalid_token: str) -> None:
    """Test getting the current user with an invalid token."""
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(invalid_token)

    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user() -> None:
    """Test getting a non-existent user."""
    # Arrange
    # Create a token with a non-existent user ID
    token = create_access_token(data={"sub": "nonexistent-user-id"})

    # Mock the User.get_or_none to return None (user not found)
    with mock.patch.object(User, "get_or_none", new=mock.AsyncMock(return_value=None)):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(token)

        assert excinfo.value.status_code == 401
        assert "CITIZEN NOT FOUND IN STATE RECORDS" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_optional_user_valid_token() -> None:
    """Test getting an optional user with a valid token."""
    # Arrange
    user_id = "test-user-id"
    token = create_access_token(data={"sub": user_id})

    # Create a mock user
    mock_user = mock.AsyncMock()
    mock_user.id = user_id
    mock_user.is_locked = False

    # Mock get_current_user to return our mock user
    with mock.patch("backend.utils.auth.get_current_user", return_value=mock_user):
        # Act
        user = await get_optional_user(token)

        # Assert
        assert user is not None
        assert user.id == user_id


@pytest.mark.asyncio
async def test_get_optional_user_invalid_token(invalid_token: str) -> None:
    """Test getting an optional user with an invalid token."""
    # Act
    user = await get_optional_user(invalid_token)

    # Assert
    assert user is None


@pytest.mark.asyncio
async def test_get_optional_user_no_token() -> None:
    """Test getting an optional user with no token."""
    # Act & Assert - this is a simple case we can test directly
    result = await get_optional_user(None)
    assert result is None
