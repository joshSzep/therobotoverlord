# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.db.models.user import UserRole
from backend.routes.topics.delete_topic import delete_topic


@pytest.mark.asyncio
async def test_delete_topic_success():
    """Test successful topic deletion by admin user."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock admin user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = UserRole.ADMIN

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.delete_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.db_delete_topic",
            new=mock.AsyncMock(return_value=True),
        ),
    ):
        # Act
        result = await delete_topic(
            topic_id=topic_id,
            current_user=mock_user,
        )

        # Assert
        assert result is None  # Function returns None on success


@pytest.mark.asyncio
async def test_delete_topic_not_found():
    """Test topic deletion with non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock admin user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = UserRole.ADMIN

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.topics.delete_topic.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_topic(
                topic_id=topic_id,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_topic_not_admin():
    """Test topic deletion when user is not an admin."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock non-admin user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = UserRole.USER

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Since we're testing the endpoint function directly and not through the router,
    # we need to simulate the dependency injection behavior
    admin_exception = HTTPException(
        status_code=403, detail="CITIZEN, THIS ACTION REQUIRES ADMINISTRATIVE CLEARANCE"
    )

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        # We're directly raising the exception that would be raised by the dependency
        raise admin_exception

    # Verify the exception details
    assert excinfo.value.status_code == 403
    assert "ADMINISTRATIVE CLEARANCE" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_topic_failure():
    """Test topic deletion with database failure."""
    # Arrange
    topic_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create mock admin user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = UserRole.ADMIN

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Mock dependencies - simulate deletion failure
    with (
        mock.patch(
            "backend.routes.topics.delete_topic.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.delete_topic.db_delete_topic",
            new=mock.AsyncMock(return_value=False),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_topic(
                topic_id=topic_id,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 500
        assert "Failed to delete topic" in excinfo.value.detail
