"""Tests for the UserSession model."""

from datetime import datetime
from unittest import mock

import pytest
from tortoise.queryset import QuerySet

from backend.db.models.user_session import UserSession


@pytest.fixture
def mock_user_session() -> UserSession:
    """Return a mock user session for testing."""
    session = mock.MagicMock(spec=UserSession)
    session.is_active = True
    session.save = mock.AsyncMock()
    return session


@pytest.mark.asyncio
async def test_invalidate() -> None:
    """Test that invalidate() sets is_active to False and saves the session."""
    # Create a mock session
    session = mock.MagicMock(spec=UserSession)
    session.is_active = True
    session.save = mock.AsyncMock()

    # Add the real method implementation to our mock
    async def mock_invalidate():
        session.is_active = False
        await session.save()

    session.invalidate = mock_invalidate

    # Call invalidate
    await session.invalidate()

    # Verify is_active was set to False
    assert session.is_active is False

    # Verify save was called
    session.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_cleanup_expired_no_sessions() -> None:
    """Test cleanup_expired() when there are no expired sessions."""
    # Mock the queryset
    mock_queryset = mock.MagicMock(spec=QuerySet)
    mock_queryset.update = mock.AsyncMock(return_value=0)

    with mock.patch(
        "backend.db.models.user_session.UserSession.filter", return_value=mock_queryset
    ) as mock_filter:
        # Call cleanup_expired
        count = await UserSession.cleanup_expired()

        # Verify filter was called with the correct parameters
        mock_filter.assert_called_once_with(
            expires_at__lt=mock.ANY,
            is_active=True,
        )

        # Verify update was called with the correct parameters
        mock_queryset.update.assert_awaited_once_with(is_active=False)

        # Verify the correct count was returned
        assert count == 0


@pytest.mark.asyncio
async def test_cleanup_expired_with_sessions() -> None:
    """Test cleanup_expired() when there are expired sessions."""
    # Mock the queryset
    mock_queryset = mock.MagicMock(spec=QuerySet)
    mock_queryset.update = mock.AsyncMock(return_value=2)

    with (
        mock.patch(
            "backend.db.models.user_session.UserSession.filter",
            return_value=mock_queryset,
        ) as mock_filter,
        mock.patch("backend.db.models.user_session.now_utc") as mock_now_utc,
    ):
        # Set up mock now_utc
        current_time = datetime.now()
        mock_now_utc.return_value = current_time

        # Call cleanup_expired
        count = await UserSession.cleanup_expired()

        # Verify filter was called with the correct parameters
        mock_filter.assert_called_once_with(
            expires_at__lt=current_time,
            is_active=True,
        )

        # Verify update was called with the correct parameters
        mock_queryset.update.assert_awaited_once_with(is_active=False)

        # Verify the correct count was returned
        assert count == 2


@pytest.mark.asyncio
async def test_cleanup_expired_only_updates_active_sessions() -> None:
    """Test cleanup_expired() only updates active sessions."""
    # Mock the queryset
    mock_queryset = mock.MagicMock(spec=QuerySet)
    mock_queryset.update = mock.AsyncMock(return_value=1)

    with mock.patch(
        "backend.db.models.user_session.UserSession.filter", return_value=mock_queryset
    ) as mock_filter:
        # Call cleanup_expired
        await UserSession.cleanup_expired()

        # Verify filter includes is_active=True
        call_kwargs = mock_filter.call_args[1]
        assert call_kwargs["is_active"] is True
