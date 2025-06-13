# Standard library imports
from datetime import datetime
from datetime import timedelta
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import DoesNotExist

# Project-specific imports
from backend.db.models.user import User
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.create_user_session import create_user_session
from backend.schemas.user import UserSessionSchema


@pytest.fixture
def mock_user() -> mock.MagicMock:
    """Returns a mock User object."""
    user = mock.MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.username = "test_user"
    user.last_login = None
    return user


@pytest.fixture
def mock_user_session() -> mock.MagicMock:
    """Returns a mock UserSession object."""
    session = mock.MagicMock(spec=UserSession)
    session.id = uuid.uuid4()
    session.user_id = uuid.uuid4()
    session.token = "test_token"
    session.ip_address = "127.0.0.1"
    session.user_agent = "Test User Agent"
    session.expires_at = datetime.now() + timedelta(days=7)
    session.is_active = True
    return session


@pytest.fixture
def mock_session_schema() -> mock.MagicMock:
    """Returns a mock UserSessionSchema object."""
    return mock.MagicMock(spec=UserSessionSchema)


@pytest.mark.asyncio
async def test_create_user_session_success(
    mock_user, mock_user_session, mock_session_schema
) -> None:
    """
    Test create_user_session successfully creates a session.
    """
    # Arrange
    user_id = mock_user.id
    ip_address = "192.168.1.1"
    user_agent = "Test Browser"
    expires_days = 14

    # Mock the dependencies
    with (
        mock.patch.object(
            User, "get", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get_user,
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(return_value=mock_user_session)
        ) as mock_create_session,
        mock.patch.object(mock_user, "save", new=mock.AsyncMock()) as mock_save_user,
        mock.patch(
            "backend.db_functions.user_sessions.create_user_session.user_session_to_schema",
            new=mock.AsyncMock(return_value=mock_session_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.user_sessions.create_user_session.secrets.token_urlsafe",
            return_value="secure_token_123",
        ) as mock_token_generator,
        mock.patch(
            "backend.db_functions.user_sessions.create_user_session.now_utc",
            return_value=datetime.now(),
        ) as mock_now,
    ):
        # Act
        result = await create_user_session(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_days=expires_days,
        )

        # Assert
        assert result == mock_session_schema
        mock_get_user.assert_called_once_with(id=user_id)
        mock_create_session.assert_called_once()
        mock_save_user.assert_called_once()
        mock_converter.assert_called_once_with(mock_user_session)
        mock_token_generator.assert_called_once_with(32)
        assert mock_now.call_count >= 1

        # Verify user's last_login was updated
        assert mock_user.last_login is not None


@pytest.mark.asyncio
async def test_create_user_session_default_values(
    mock_user, mock_user_session, mock_session_schema
) -> None:
    """
    Test create_user_session with default parameter values.
    """
    # Arrange
    user_id = mock_user.id

    # Mock the dependencies
    with (
        mock.patch.object(
            User, "get", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get_user,
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(return_value=mock_user_session)
        ) as mock_create_session,
        mock.patch.object(mock_user, "save", new=mock.AsyncMock()),
        mock.patch(
            "backend.db_functions.user_sessions.create_user_session.user_session_to_schema",
            new=mock.AsyncMock(return_value=mock_session_schema),
        ),
        mock.patch(
            "backend.db_functions.user_sessions.create_user_session.secrets.token_urlsafe",
            return_value="secure_token_123",
        ),
        mock.patch(
            "backend.db_functions.user_sessions.create_user_session.now_utc",
            return_value=datetime.now(),
        ),
    ):
        # Act
        result = await create_user_session(user_id=user_id)

        # Assert
        assert result == mock_session_schema
        mock_get_user.assert_called_once_with(id=user_id)
        mock_create_session.assert_called_once()
        # Verify default values were used
        args, kwargs = mock_create_session.call_args
        assert kwargs["ip_address"] == "0.0.0.0"
        assert kwargs["user_agent"] == "Unknown"
        assert kwargs["is_active"] is True


@pytest.mark.asyncio
async def test_create_user_session_user_not_found() -> None:
    """
    Test create_user_session raises ValueError when user is not found.
    """
    # Arrange
    user_id = uuid.uuid4()

    # Mock the dependencies
    with (
        mock.patch.object(
            User, "get", new=mock.AsyncMock(side_effect=DoesNotExist("User not found"))
        ) as mock_get_user,
    ):
        # Act & Assert
        with pytest.raises(ValueError, match=f"User with ID {user_id} not found"):
            await create_user_session(user_id=user_id)

        mock_get_user.assert_called_once_with(id=user_id)


@pytest.mark.asyncio
async def test_create_user_session_database_error(mock_user) -> None:
    """
    Test create_user_session handles database errors during session creation.
    """
    # Arrange
    user_id = mock_user.id
    db_error = Exception("Database connection error")

    # Mock the dependencies
    with (
        mock.patch.object(
            User, "get", new=mock.AsyncMock(return_value=mock_user)
        ) as mock_get_user,
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(side_effect=db_error)
        ) as mock_create_session,
    ):
        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            await create_user_session(user_id=user_id)

        mock_get_user.assert_called_once_with(id=user_id)
        mock_create_session.assert_called_once()
