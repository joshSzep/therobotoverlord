# Standard library imports
from datetime import datetime
from datetime import timedelta
import secrets
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.get_session_by_token import get_session_by_token
from backend.schemas.user import UserSessionSchema


@pytest.fixture
def mock_user_session() -> mock.MagicMock:
    session = mock.MagicMock(spec=UserSession)
    session.id = uuid.uuid4()
    session.user_id = uuid.uuid4()
    session.session_token = secrets.token_hex(32)
    session.ip_address = "192.168.1.1"
    session.user_agent = "Mozilla/5.0"
    session.is_active = True
    session.expires_at = datetime.now() + timedelta(days=7)
    session.created_at = mock.MagicMock()
    # Add fetch_related method for the converter
    session.fetch_related = mock.AsyncMock()
    # Mock the user property
    session.user = mock.MagicMock()
    session.user.id = session.user_id
    return session


@pytest.fixture
def mock_session_schema(mock_user_session) -> UserSessionSchema:
    return UserSessionSchema(
        id=mock_user_session.id,
        session_token=mock_user_session.session_token,
        ip_address=mock_user_session.ip_address,
        user_agent=mock_user_session.user_agent,
        is_active=mock_user_session.is_active,
        expires_at=mock_user_session.expires_at,
        created_at=mock_user_session.created_at,
        user_id=mock_user_session.user_id,
    )


@pytest.mark.asyncio
async def test_get_session_by_token_success(
    mock_user_session, mock_session_schema
) -> None:
    # Arrange
    test_token = mock_user_session.session_token

    # Mock the database query - RULE #10 compliance: only operates on UserSession model
    with (
        mock.patch.object(
            UserSession,
            "get_or_none",
            return_value=mock.MagicMock(),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.get_session_by_token.user_session_to_schema",
            new=mock.AsyncMock(return_value=mock_session_schema),
        ) as mock_converter,
    ):
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=mock_user_session)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act
        result = await get_session_by_token(test_token)

        # Assert
        assert result is not None
        assert result.id == mock_user_session.id
        assert result.session_token == test_token
        assert result.ip_address == mock_user_session.ip_address
        assert result.user_agent == mock_user_session.user_agent
        assert result.is_active is True

        # Verify function calls
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")
        mock_converter.assert_called_once_with(mock_user_session)


@pytest.mark.asyncio
async def test_get_session_by_token_not_found() -> None:
    # Arrange
    test_token = secrets.token_hex(32)

    # Mock the database query
    with mock.patch.object(
        UserSession, "get_or_none", return_value=mock.MagicMock()
    ) as mock_get:
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=None)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act
        result = await get_session_by_token(test_token)

        # Assert
        assert result is None

        # Verify function calls
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")


@pytest.mark.asyncio
async def test_get_session_by_token_inactive() -> None:
    # Arrange
    test_token = secrets.token_hex(32)

    # Mock the database query to return None (inactive session)
    with mock.patch.object(
        UserSession, "get_or_none", return_value=mock.MagicMock()
    ) as mock_get:
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=None)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act
        result = await get_session_by_token(test_token)

        # Assert
        assert result is None

        # Verify function calls
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")


@pytest.mark.asyncio
async def test_get_session_by_token_database_error() -> None:
    # Arrange
    test_token = secrets.token_hex(32)
    db_error = OperationalError("Database error")

    # Mock the database query to raise an error
    with mock.patch.object(
        UserSession, "get_or_none", side_effect=db_error
    ) as mock_get:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await get_session_by_token(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )


@pytest.mark.asyncio
async def test_get_session_by_token_prefetch_error(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    prefetch_error = OperationalError("Prefetch error")

    # Mock the database query
    with mock.patch.object(
        UserSession, "get_or_none", return_value=mock.MagicMock()
    ) as mock_get:
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(side_effect=prefetch_error)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await get_session_by_token(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == prefetch_error
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")


@pytest.mark.asyncio
async def test_get_session_by_token_converter_error(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            UserSession, "get_or_none", return_value=mock.MagicMock()
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.get_session_by_token.user_session_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
    ):
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=mock_user_session)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await get_session_by_token(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")
        mock_converter.assert_called_once_with(mock_user_session)
