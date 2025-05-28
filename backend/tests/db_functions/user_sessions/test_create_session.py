# Standard library imports
from datetime import datetime
from datetime import timedelta
import secrets
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.user_session import UserSession
from backend.db_functions.user_sessions.create_session import create_session
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
    session.updated_at = mock.MagicMock()
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
    )


@pytest.mark.asyncio
async def test_create_session_success(mock_user_session, mock_session_schema) -> None:
    # Arrange
    test_user_id = mock_user_session.user_id
    test_ip_address = mock_user_session.ip_address
    test_user_agent = mock_user_session.user_agent
    test_expires_in_days = 7
    mock_token = mock_user_session.session_token
    mock_now = datetime.now()
    mock_expires_at = mock_now + timedelta(days=test_expires_in_days)

    # Mock the database query - RULE #10 compliance: only operates on UserSession model
    with (
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(return_value=mock_user_session)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.user_session_to_schema",
            new=mock.AsyncMock(return_value=mock_session_schema),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.secrets.token_hex",
            return_value=mock_token,
        ) as mock_token_hex,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.now_utc",
            return_value=mock_now,
        ) as mock_now_utc,
    ):
        # Act
        result = await create_session(
            user_id=test_user_id,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            expires_in_days=test_expires_in_days,
        )

        # Assert
        assert result is not None
        assert result.id == mock_user_session.id
        assert result.session_token == mock_token
        assert result.ip_address == test_ip_address
        assert result.user_agent == test_user_agent
        assert result.is_active is True

        # Verify function calls
        mock_token_hex.assert_called_once_with(32)
        mock_now_utc.assert_called_once()
        mock_create.assert_called_once_with(
            user_id=test_user_id,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            session_token=mock_token,
            is_active=True,
            expires_at=mock_expires_at,
        )
        mock_converter.assert_called_once_with(mock_user_session)


@pytest.mark.asyncio
async def test_create_session_custom_expiry(
    mock_user_session, mock_session_schema
) -> None:
    # Arrange
    test_user_id = mock_user_session.user_id
    test_ip_address = mock_user_session.ip_address
    test_user_agent = mock_user_session.user_agent
    test_expires_in_days = 30  # Custom expiry
    mock_token = mock_user_session.session_token
    mock_now = datetime.now()
    mock_expires_at = mock_now + timedelta(days=test_expires_in_days)

    # Mock the database query
    with (
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(return_value=mock_user_session)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.user_session_to_schema",
            new=mock.AsyncMock(return_value=mock_session_schema),
        ),
        mock.patch(
            "backend.db_functions.user_sessions.create_session.secrets.token_hex",
            return_value=mock_token,
        ),
        mock.patch(
            "backend.db_functions.user_sessions.create_session.now_utc",
            return_value=mock_now,
        ),
    ):
        # Act
        result = await create_session(
            user_id=test_user_id,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            expires_in_days=test_expires_in_days,
        )

        # Assert
        assert result is not None

        # Verify function calls with custom expiry
        mock_create.assert_called_once_with(
            user_id=test_user_id,
            ip_address=test_ip_address,
            user_agent=test_user_agent,
            session_token=mock_token,
            is_active=True,
            expires_at=mock_expires_at,
        )


@pytest.mark.asyncio
async def test_create_session_database_error() -> None:
    # Arrange
    test_user_id = uuid.uuid4()
    test_ip_address = "192.168.1.1"
    test_user_agent = "Mozilla/5.0"
    test_expires_in_days = 7
    mock_token = secrets.token_hex(32)
    db_error = IntegrityError("Database error")

    # Mock the database query
    with (
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(side_effect=db_error)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.secrets.token_hex",
            return_value=mock_token,
        ) as mock_token_hex,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.now_utc",
            return_value=datetime.now(),
        ) as mock_now_utc,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_session(
                user_id=test_user_id,
                ip_address=test_ip_address,
                user_agent=test_user_agent,
                expires_in_days=test_expires_in_days,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_token_hex.assert_called_once_with(32)
        mock_now_utc.assert_called_once()
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_converter_error(mock_user_session) -> None:
    # Arrange
    test_user_id = mock_user_session.user_id
    test_ip_address = mock_user_session.ip_address
    test_user_agent = mock_user_session.user_agent
    test_expires_in_days = 7
    mock_token = mock_user_session.session_token
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(
            UserSession, "create", new=mock.AsyncMock(return_value=mock_user_session)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.user_session_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
        mock.patch(
            "backend.db_functions.user_sessions.create_session.secrets.token_hex",
            return_value=mock_token,
        ),
        mock.patch(
            "backend.db_functions.user_sessions.create_session.now_utc",
            return_value=datetime.now(),
        ),
    ):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await create_session(
                user_id=test_user_id,
                ip_address=test_ip_address,
                user_agent=test_user_agent,
                expires_in_days=test_expires_in_days,
            )

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_create.assert_called_once()
        mock_converter.assert_called_once_with(mock_user_session)
