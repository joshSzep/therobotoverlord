# Standard library imports
import secrets
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.deactivate_session import deactivate_session


@pytest.fixture
def mock_user_session() -> mock.MagicMock:
    session = mock.MagicMock(spec=UserSession)
    session.id = uuid.uuid4()
    session.user_id = uuid.uuid4()
    session.session_token = secrets.token_hex(32)
    session.ip_address = "192.168.1.1"
    session.user_agent = "Mozilla/5.0"
    session.is_active = True
    session.save = mock.AsyncMock()
    return session


@pytest.mark.asyncio
async def test_deactivate_session_success(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token

    # Mock the database query
    with mock.patch.object(
        UserSession, "get_or_none", new=mock.AsyncMock(return_value=mock_user_session)
    ) as mock_get:
        # Act
        result = await deactivate_session(test_token)

        # Assert
        assert result is True
        assert mock_user_session.is_active is False
        mock_get.assert_called_once_with(session_token=test_token)
        mock_user_session.save.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_session_not_found() -> None:
    # Arrange
    test_token = secrets.token_hex(32)

    # Mock the database query to return None (session not found)
    with mock.patch.object(
        UserSession, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await deactivate_session(test_token)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(session_token=test_token)


@pytest.mark.asyncio
async def test_deactivate_session_database_error() -> None:
    # Arrange
    test_token = secrets.token_hex(32)
    db_error = OperationalError("Database error")

    # Mock the database query to raise an error
    with mock.patch.object(
        UserSession, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await deactivate_session(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(session_token=test_token)


@pytest.mark.asyncio
async def test_deactivate_session_save_error(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    save_error = OperationalError("Save error")
    mock_user_session.save = mock.AsyncMock(side_effect=save_error)

    # Mock the database query
    with mock.patch.object(
        UserSession, "get_or_none", new=mock.AsyncMock(return_value=mock_user_session)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await deactivate_session(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        assert mock_user_session.is_active is False
        mock_get.assert_called_once_with(session_token=test_token)
        mock_user_session.save.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_session_already_inactive(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    mock_user_session.is_active = False  # Already inactive

    # Mock the database query
    with mock.patch.object(
        UserSession, "get_or_none", new=mock.AsyncMock(return_value=mock_user_session)
    ) as mock_get:
        # Act
        result = await deactivate_session(test_token)

        # Assert
        assert result is True
        assert mock_user_session.is_active is False
        mock_get.assert_called_once_with(session_token=test_token)
        # Still saves even if already inactive
        mock_user_session.save.assert_called_once()
