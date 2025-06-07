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
from backend.db_functions.user_sessions.validate_session import validate_session
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
async def test_validate_session_success(mock_user_session, mock_session_schema) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    current_time = datetime.now()
    mock_user_session.expires_at = current_time + timedelta(days=1)  # Not expired

    # Mock the database query
    with (
        mock.patch.object(
            UserSession,
            "get_or_none",
            return_value=mock.MagicMock(),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.user_session_to_schema",
            return_value=mock_session_schema,
        ),
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.now_utc",
            return_value=current_time,
        ) as mock_now_utc,
    ):
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=mock_user_session)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act
        result = await validate_session(test_token)

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
        mock_now_utc.assert_called_once()
        # Session should not be saved since it's not expired
        mock_user_session.save.assert_not_called()


@pytest.mark.asyncio
async def test_validate_session_not_found() -> None:
    # Arrange
    test_token = secrets.token_hex(32)

    # Mock the database query
    with (
        mock.patch.object(
            UserSession,
            "get_or_none",
            return_value=mock.MagicMock(),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.now_utc",
            return_value=datetime.now(),
        ),
    ):
        # Set up the prefetch_related chain to return None
        prefetch_mock = mock.AsyncMock(return_value=None)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act
        result = await validate_session(test_token)

        # Assert
        assert result is None

        # Verify function calls
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")


@pytest.mark.asyncio
async def test_validate_session_expired(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    current_time = datetime.now()
    mock_user_session.expires_at = current_time - timedelta(days=1)  # Expired
    mock_user_session.save = mock.AsyncMock()

    # Mock the database query
    with (
        mock.patch.object(
            UserSession,
            "get_or_none",
            return_value=mock.MagicMock(),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.now_utc",
            return_value=current_time,
        ) as mock_now_utc,
    ):
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=mock_user_session)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act
        result = await validate_session(test_token)

        # Assert
        assert result is None
        assert mock_user_session.is_active is False  # Should be deactivated

        # Verify function calls
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")
        mock_now_utc.assert_called_once()
        # Session should be saved with is_active=False
        mock_user_session.save.assert_called_once()


@pytest.mark.asyncio
async def test_validate_session_database_error() -> None:
    # Arrange
    test_token = secrets.token_hex(32)
    db_error = OperationalError("Database error")

    # Mock the database query to raise an error
    with mock.patch.object(
        UserSession, "get_or_none", side_effect=db_error
    ) as mock_get:
        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await validate_session(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )


@pytest.mark.asyncio
async def test_validate_session_prefetch_error() -> None:
    # Arrange
    test_token = secrets.token_hex(32)
    prefetch_error = OperationalError("Prefetch error")

    # Mock the database query
    with mock.patch.object(
        UserSession, "get_or_none", return_value=mock.MagicMock()
    ) as mock_get:
        # Set up the prefetch_related chain to raise an error
        prefetch_mock = mock.AsyncMock(side_effect=prefetch_error)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await validate_session(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == prefetch_error
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")


@pytest.mark.asyncio
async def test_validate_session_save_error(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    current_time = datetime.now()
    mock_user_session.expires_at = current_time - timedelta(days=1)  # Expired
    save_error = OperationalError("Save error")
    mock_user_session.save = mock.AsyncMock(side_effect=save_error)

    # Mock the database query
    with (
        mock.patch.object(
            UserSession,
            "get_or_none",
            return_value=mock.MagicMock(),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.now_utc",
            return_value=current_time,
        ),
    ):
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=mock_user_session)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await validate_session(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        assert mock_user_session.is_active is False  # Should be deactivated
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")
        mock_user_session.save.assert_called_once()


@pytest.mark.asyncio
async def test_validate_session_converter_error(mock_user_session) -> None:
    # Arrange
    test_token = mock_user_session.session_token
    current_time = datetime.now()
    mock_user_session.expires_at = current_time + timedelta(days=1)  # Not expired
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            UserSession,
            "get_or_none",
            return_value=mock.MagicMock(),
        ) as mock_get,
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.user_session_to_schema",
            side_effect=converter_error,
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.user_sessions.validate_session.now_utc",
            return_value=current_time,
        ),
    ):
        # Set up the prefetch_related chain
        prefetch_mock = mock.AsyncMock(return_value=mock_user_session)
        mock_get.return_value.prefetch_related = prefetch_mock

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await validate_session(test_token)

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_get.assert_called_once_with(
            session_token=test_token,
            is_active=True,
        )
        mock_get.return_value.prefetch_related.assert_called_once_with("user")
        mock_converter.assert_called_once_with(mock_user_session)
