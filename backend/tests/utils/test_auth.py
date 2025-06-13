# Standard library imports
from datetime import datetime
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
from fastapi import status
import jwt
import pytest

# Project-specific imports
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.utils.auth import decode_token
from backend.utils.auth import get_current_user
from backend.utils.auth import get_optional_user
from backend.utils.settings import settings


@pytest.fixture
def mock_user() -> mock.MagicMock:
    """Returns a mock User object."""
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.username = "test_user"
    user.is_locked = False
    return user


@pytest.fixture
def mock_user_session() -> mock.MagicMock:
    """Returns a mock UserSession object."""
    session = mock.MagicMock(spec=UserSession)
    session.id = uuid.uuid4()
    session.user_id = uuid.uuid4()
    session.is_active = True
    return session


@pytest.fixture
def user_data() -> dict:
    """Returns sample user data for token creation."""
    return {"sub": str(uuid.uuid4()), "username": "test_user"}


@pytest.fixture
def mock_now_utc():
    """Mock the now_utc function to return a fixed datetime."""
    with mock.patch("backend.utils.auth.now_utc") as mock_now:
        mock_now.return_value = datetime(2025, 1, 1, 12, 0, 0)
        yield mock_now


def test_decode_token_valid(user_data):
    """Test decoding a valid token."""
    # Arrange
    token = jwt.encode(
        user_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Act
    result = decode_token(token)

    # Assert
    assert result == user_data


def test_decode_token_invalid_signature():
    """Test decoding a token with invalid signature."""
    # Arrange
    token = jwt.encode(
        {"sub": "test"},
        "wrong_secret",
        algorithm=settings.JWT_ALGORITHM,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "AUTHENTICATION TOKEN HAS FAILED INSPECTION" in exc_info.value.detail


def test_decode_token_expired():
    """Test decoding an expired token."""
    # Arrange
    expired_payload = {
        "sub": "test",
        "exp": datetime(2020, 1, 1).timestamp(),  # Expired
    }
    token = jwt.encode(
        expired_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "AUTHENTICATION TOKEN HAS FAILED INSPECTION" in exc_info.value.detail


def test_decode_token_invalid_payload():
    """Test decoding a token with invalid payload structure."""
    # This test is a bit tricky since PyJWT will validate most payloads
    # We'll mock jwt.decode to return a non-dict value
    with mock.patch("jwt.decode", return_value="not_a_dict"):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            decode_token("dummy_token")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "AUTHENTICATION TOKEN HAS FAILED INSPECTION" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_valid(mock_user):
    """Test getting current user with valid token and active session."""
    # Arrange
    user_id = str(mock_user.id)
    token = "valid_token"

    with (
        mock.patch(
            "backend.utils.auth.decode_token", return_value={"sub": user_id}
        ) as mock_decode,
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get_user,
        mock.patch.object(
            UserSession, "filter", return_value=mock.AsyncMock()
        ) as mock_filter,
    ):
        mock_filter.return_value.exists = mock.AsyncMock(return_value=True)

        # Act
        result = await get_current_user(token)

        # Assert
        assert result == mock_user
        mock_decode.assert_called_once_with(token)
        mock_get_user.assert_called_once_with(id=user_id)
        mock_filter.assert_called_once_with(user_id=user_id, is_active=True)
        mock_filter.return_value.exists.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_no_sub_claim():
    """Test getting current user with token missing sub claim."""
    # Arrange
    token = "invalid_token"

    with mock.patch("backend.utils.auth.decode_token", return_value={}):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "IDENTITY DOCUMENTS REQUIRE VERIFICATION" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    """Test getting current user when user is not found."""
    # Arrange
    user_id = str(uuid.uuid4())
    token = "valid_token"

    with (
        mock.patch("backend.utils.auth.decode_token", return_value={"sub": user_id}),
        mock.patch.object(User, "get_or_none", new=mock.AsyncMock(return_value=None)),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "CITIZEN NOT FOUND IN STATE RECORDS" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_locked_account(mock_user):
    """Test getting current user with locked account."""
    # Arrange
    user_id = str(mock_user.id)
    token = "valid_token"
    mock_user.is_locked = True

    with (
        mock.patch("backend.utils.auth.decode_token", return_value={"sub": user_id}),
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == status.HTTP_410_GONE
        assert "ACCOUNT HAS BEEN LOCKED FOR RECALIBRATION" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_no_active_session(mock_user):
    """Test getting current user with no active session."""
    # Arrange
    user_id = str(mock_user.id)
    token = "valid_token"

    with (
        mock.patch("backend.utils.auth.decode_token", return_value={"sub": user_id}),
        mock.patch.object(
            User, "get_or_none", new=mock.AsyncMock(return_value=mock_user)
        ),
        mock.patch.object(
            UserSession, "filter", return_value=mock.AsyncMock()
        ) as mock_filter,
    ):
        mock_filter.return_value.exists = mock.AsyncMock(return_value=False)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "SESSION HAS EXPIRED OR BEEN TERMINATED" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_optional_user_with_token(mock_user):
    """Test getting optional user with valid token."""
    # Arrange
    token = "valid_token"

    with mock.patch(
        "backend.utils.auth.get_current_user",
        new=mock.AsyncMock(return_value=mock_user),
    ) as mock_get_user:
        # Act
        result = await get_optional_user(token)

        # Assert
        assert result == mock_user
        mock_get_user.assert_called_once_with(token)


@pytest.mark.asyncio
async def test_get_optional_user_without_token():
    """Test getting optional user without token."""
    # Act
    result = await get_optional_user(None)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_optional_user_with_invalid_token():
    """Test getting optional user with invalid token."""
    # Arrange
    token = "invalid_token"
    http_exception = HTTPException(status_code=401, detail="Invalid token")

    with mock.patch(
        "backend.utils.auth.get_current_user",
        new=mock.AsyncMock(side_effect=http_exception),
    ):
        # Act
        result = await get_optional_user(token)

        # Assert
        assert result is None
