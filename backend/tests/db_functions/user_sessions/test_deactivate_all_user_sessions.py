# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.deactivate_all_user_sessions import (
    deactivate_all_user_sessions,
)


@pytest.fixture
def mock_user_sessions() -> list[mock.MagicMock]:
    sessions = []
    for _ in range(3):
        session = mock.MagicMock(spec=UserSession)
        session.id = uuid.uuid4()
        session.user_id = uuid.uuid4()
        session.is_active = True
        session.save = mock.AsyncMock()
        sessions.append(session)

    # Make all sessions have the same user_id
    user_id = uuid.uuid4()
    for session in sessions:
        session.user_id = user_id

    return sessions


@pytest.mark.asyncio
async def test_deactivate_all_user_sessions_success(mock_user_sessions) -> None:
    # Arrange
    test_user_id = mock_user_sessions[0].user_id

    # Mock the database query
    with mock.patch.object(
        UserSession, "filter", new=mock.AsyncMock(return_value=mock_user_sessions)
    ) as mock_filter:
        # Act
        result = await deactivate_all_user_sessions(test_user_id)

        # Assert
        assert result == len(mock_user_sessions)
        mock_filter.assert_called_once_with(user_id=test_user_id, is_active=True)

        # Verify all sessions were deactivated and saved
        for session in mock_user_sessions:
            assert session.is_active is False
            session.save.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_all_user_sessions_no_sessions() -> None:
    # Arrange
    test_user_id = uuid.uuid4()

    # Mock the database query to return empty list
    with mock.patch.object(
        UserSession, "filter", new=mock.AsyncMock(return_value=[])
    ) as mock_filter:
        # Act
        result = await deactivate_all_user_sessions(test_user_id)

        # Assert
        assert result == 0
        mock_filter.assert_called_once_with(user_id=test_user_id, is_active=True)


@pytest.mark.asyncio
async def test_deactivate_all_user_sessions_filter_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    db_error = OperationalError("Database error")

    # Mock the database query to raise an error
    with mock.patch.object(
        UserSession, "filter", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await deactivate_all_user_sessions(test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(user_id=test_user_id, is_active=True)


@pytest.mark.asyncio
async def test_deactivate_all_user_sessions_save_error(mock_user_sessions) -> None:
    # Arrange
    test_user_id = mock_user_sessions[0].user_id
    save_error = OperationalError("Save error")

    # Make the second session raise an error on save
    mock_user_sessions[1].save = mock.AsyncMock(side_effect=save_error)

    # Mock the database query
    with mock.patch.object(
        UserSession, "filter", new=mock.AsyncMock(return_value=mock_user_sessions)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await deactivate_all_user_sessions(test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_filter.assert_called_once_with(user_id=test_user_id, is_active=True)

        # First session should be deactivated and saved
        assert mock_user_sessions[0].is_active is False
        mock_user_sessions[0].save.assert_called_once()

        # Second session should be deactivated but save failed
        assert mock_user_sessions[1].is_active is False
        mock_user_sessions[1].save.assert_called_once()

        # Third session should not be processed
        assert mock_user_sessions[2].is_active is True
        mock_user_sessions[2].save.assert_not_called()
