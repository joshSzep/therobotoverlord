# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.delete_user_session import delete_user_session


@pytest.fixture
def mock_user_session() -> mock.MagicMock:
    """Returns a mock UserSession object."""
    session = mock.MagicMock(spec=UserSession)
    session.id = uuid.uuid4()
    session.user_id = uuid.uuid4()
    session.session_token = "test_token"
    session.ip_address = "127.0.0.1"
    session.user_agent = "Test User Agent"
    session.is_active = True
    session.save = mock.AsyncMock()
    return session


@pytest.mark.asyncio
async def test_delete_user_session_success(mock_user_session) -> None:
    """
    Test delete_user_session successfully deactivates a session with a valid token.
    """
    # Arrange
    token = "valid_token"

    # Mock the dependencies
    with mock.patch.object(
        UserSession, "filter", return_value=mock.AsyncMock()
    ) as mock_filter:
        mock_filter.return_value.first = mock.AsyncMock(return_value=mock_user_session)

        # Act
        result = await delete_user_session(token=token)

        # Assert
        assert result is True
        mock_filter.assert_called_once_with(session_token=token)
        mock_filter.return_value.first.assert_called_once()
        assert mock_user_session.is_active is False
        mock_user_session.save.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_session_invalid_token() -> None:
    """
    Test delete_user_session returns False when session with token is not found.
    """
    # Arrange
    token = "invalid_token"

    # Mock the dependencies
    with mock.patch.object(
        UserSession, "filter", return_value=mock.AsyncMock()
    ) as mock_filter:
        mock_filter.return_value.first = mock.AsyncMock(return_value=None)

        # Act
        result = await delete_user_session(token=token)

        # Assert
        assert result is False
        mock_filter.assert_called_once_with(session_token=token)
        mock_filter.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_session_database_error(mock_user_session) -> None:
    """
    Test delete_user_session handles database errors during session deactivation.
    """
    # Arrange
    token = "valid_token"
    db_error = OperationalError("Database connection error")

    # Mock the dependencies
    with mock.patch.object(
        UserSession, "filter", return_value=mock.AsyncMock()
    ) as mock_filter:
        mock_filter.return_value.first = mock.AsyncMock(return_value=mock_user_session)
        mock_user_session.save.side_effect = db_error

        # Act & Assert
        with pytest.raises(OperationalError, match="Database connection error"):
            await delete_user_session(token=token)

        mock_filter.assert_called_once_with(session_token=token)
        mock_filter.return_value.first.assert_called_once()
        assert mock_user_session.is_active is False
