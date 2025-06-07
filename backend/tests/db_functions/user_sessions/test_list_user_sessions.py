# Standard library imports
from typing import List
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.list_user_sessions import list_user_sessions
from backend.schemas.user import UserSessionSchema


@pytest.fixture
def mock_user_sessions() -> List[mock.MagicMock]:
    sessions = []
    user_id = uuid.uuid4()

    for i in range(5):
        session = mock.MagicMock(spec=UserSession)
        session.id = uuid.uuid4()
        session.user_id = user_id
        session.ip_address = f"192.168.1.{i + 1}"
        session.user_agent = f"Mozilla/5.0 Test Browser {i + 1}"
        session.session_token = f"token_{i + 1}"
        session.expires_at = mock.MagicMock()
        session.is_active = i < 3  # First 3 are active, last 2 are inactive
        session.created_at = mock.MagicMock()
        sessions.append(session)

    return sessions


@pytest.fixture
def mock_session_schemas(mock_user_sessions) -> List[UserSessionSchema]:
    schemas = []

    for session in mock_user_sessions:
        schema = UserSessionSchema(
            id=session.id,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            session_token=session.session_token,
            expires_at=session.expires_at,
            is_active=session.is_active,
            created_at=session.created_at,
            user_id=session.user_id,
        )
        schemas.append(schema)

    return schemas


@pytest.mark.asyncio
async def test_list_user_sessions_success(
    mock_user_sessions, mock_session_schemas
) -> None:
    # Arrange
    test_user_id = mock_user_sessions[0].user_id
    active_only = True
    skip = 0
    limit = 20

    # Only include active sessions (first 3)
    active_sessions = [s for s in mock_user_sessions if s.is_active]
    active_count = len(active_sessions)

    # Mock the query builder
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.order_by = mock.AsyncMock(return_value=active_sessions)
    mock_query.count = mock.AsyncMock(return_value=active_count)

    # Mock the converter function
    mock_converter = mock.AsyncMock()
    # Set up mock_converter to return the corresponding schema for each session
    for i, session in enumerate(mock_user_sessions):
        if session.is_active:
            mock_converter.side_effect = [
                schema for schema in mock_session_schemas if schema.is_active
            ]

    # Apply mocks
    with (
        mock.patch.object(
            UserSession, "filter", return_value=mock_query
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.list_user_sessions.user_session_to_schema",
            new=mock_converter,
        ),
    ):
        # Act
        result, count = await list_user_sessions(
            user_id=test_user_id, active_only=active_only, skip=skip, limit=limit
        )

        # Assert
        assert count == active_count
        assert len(result) == active_count

        # Verify correct query building
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.filter.assert_called_once_with(is_active=True)
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.order_by.assert_called_once_with("-created_at")

        # Verify converter was called for each active session
        assert mock_converter.call_count == active_count


@pytest.mark.asyncio
async def test_list_user_sessions_inactive(
    mock_user_sessions, mock_session_schemas
) -> None:
    # Arrange
    test_user_id = mock_user_sessions[0].user_id
    active_only = False
    skip = 0
    limit = 20

    # Include all sessions (active and inactive)
    all_sessions = mock_user_sessions
    all_count = len(all_sessions)

    # Mock the query builder
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.order_by = mock.AsyncMock(return_value=all_sessions)
    mock_query.count = mock.AsyncMock(return_value=all_count)

    # Mock the converter function
    mock_converter = mock.AsyncMock(side_effect=mock_session_schemas)

    # Apply mocks
    with (
        mock.patch.object(
            UserSession, "filter", return_value=mock_query
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.list_user_sessions.user_session_to_schema",
            new=mock_converter,
        ),
    ):
        # Act
        result, count = await list_user_sessions(
            user_id=test_user_id, active_only=active_only, skip=skip, limit=limit
        )

        # Assert
        assert count == all_count
        assert len(result) == all_count

        # Verify correct query building
        mock_filter.assert_called_once_with(user_id=test_user_id)
        # Verify is_active filter was not applied
        mock_query.filter.assert_not_called()
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.order_by.assert_called_once_with("-created_at")

        # Verify converter was called for each session
        assert mock_converter.call_count == all_count


@pytest.mark.asyncio
async def test_list_user_sessions_pagination() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    active_only = True
    skip = 1
    limit = 2

    # Create mock sessions for pagination test
    total_count = 5
    page_sessions = [mock.MagicMock(spec=UserSession) for _ in range(2)]
    page_schemas = [mock.MagicMock(spec=UserSessionSchema) for _ in range(2)]

    # Mock the query builder
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.order_by = mock.AsyncMock(return_value=page_sessions)
    mock_query.count = mock.AsyncMock(return_value=total_count)

    # Mock the converter function
    mock_converter = mock.AsyncMock(side_effect=page_schemas)

    # Apply mocks
    with (
        mock.patch.object(
            UserSession, "filter", return_value=mock_query
        ) as mock_filter,
        mock.patch(
            "backend.db_functions.user_sessions.list_user_sessions.user_session_to_schema",
            new=mock_converter,
        ),
    ):
        # Act
        result, count = await list_user_sessions(
            user_id=test_user_id, active_only=active_only, skip=skip, limit=limit
        )

        # Assert
        assert count == total_count  # Total count before pagination
        assert len(result) == len(page_sessions)  # Result count after pagination

        # Verify correct query building
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.filter.assert_called_once_with(is_active=True)
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.order_by.assert_called_once_with("-created_at")

        # Verify converter was called for each session in the page
        assert mock_converter.call_count == len(page_sessions)


@pytest.mark.asyncio
async def test_list_user_sessions_no_sessions() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    active_only = True
    skip = 0
    limit = 20

    # Mock the query builder with empty results
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.order_by = mock.AsyncMock(return_value=[])
    mock_query.count = mock.AsyncMock(return_value=0)

    # Apply mocks
    with mock.patch.object(
        UserSession, "filter", return_value=mock_query
    ) as mock_filter:
        # Act
        result, count = await list_user_sessions(
            user_id=test_user_id, active_only=active_only, skip=skip, limit=limit
        )

        # Assert
        assert count == 0
        assert len(result) == 0
        assert isinstance(result, list)

        # Verify correct query building
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.filter.assert_called_once_with(is_active=True)
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.order_by.assert_called_once_with("-created_at")


@pytest.mark.asyncio
async def test_list_user_sessions_db_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    db_error = OperationalError("Database error")

    # Mock the filter method to raise an error
    with mock.patch.object(UserSession, "filter", side_effect=db_error) as mock_filter:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await list_user_sessions(user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(user_id=test_user_id)


@pytest.mark.asyncio
async def test_list_user_sessions_count_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    count_error = OperationalError("Count error")

    # Mock the query builder with error on count
    mock_query = mock.MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count = mock.AsyncMock(side_effect=count_error)

    # Apply mocks
    with mock.patch.object(
        UserSession, "filter", return_value=mock_query
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await list_user_sessions(user_id=test_user_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == count_error
        mock_filter.assert_called_once_with(user_id=test_user_id)
        mock_query.filter.assert_called_once_with(is_active=True)
        mock_query.count.assert_called_once()
