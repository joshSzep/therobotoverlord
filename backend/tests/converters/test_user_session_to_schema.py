from datetime import datetime
from datetime import timedelta
from unittest import mock
import uuid

import pytest

from backend.converters.user_session_to_schema import user_session_to_schema
from backend.db.models.user_session import UserSession
from backend.schemas.user import UserSessionSchema


@pytest.fixture
def mock_user_session() -> mock.MagicMock:
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id

    # Create mock session
    session = mock.MagicMock(spec=UserSession)
    session.id = session_id
    session.user = mock_user
    session.ip_address = "127.0.0.1"
    session.user_agent = "Test User Agent"
    session.session_token = "test-session-token"
    session.expires_at = datetime.now() + timedelta(days=1)
    session.is_active = True
    session.created_at = datetime.now()

    return session


@pytest.mark.asyncio
async def test_user_session_to_schema(mock_user_session) -> None:
    # Convert the mock session to a schema
    schema = await user_session_to_schema(mock_user_session)

    # Verify the schema has the correct values
    assert isinstance(schema, UserSessionSchema)
    assert schema.id == mock_user_session.id
    assert schema.ip_address == mock_user_session.ip_address
    assert schema.user_agent == mock_user_session.user_agent
    assert schema.session_token == mock_user_session.session_token
    assert schema.expires_at == mock_user_session.expires_at
    assert schema.is_active == mock_user_session.is_active
    assert schema.created_at == mock_user_session.created_at
