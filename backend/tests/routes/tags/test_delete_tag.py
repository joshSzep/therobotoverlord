# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.tags.delete_tag import delete_tag


@pytest.mark.asyncio
async def test_delete_tag_success():
    """Test successful tag deletion."""
    # Arrange
    tag_id = uuid.uuid4()

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Create mock existing tag
    mock_existing_tag = mock.MagicMock()
    mock_existing_tag.id = tag_id
    mock_existing_tag.name = "Test Tag"
    mock_existing_tag.slug = "test-tag"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.tags.delete_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_existing_tag),
        ),
        mock.patch(
            "backend.routes.tags.delete_tag.get_topics_for_tag",
            new=mock.AsyncMock(return_value=[]),
        ),
        mock.patch(
            "backend.routes.tags.delete_tag.db_delete_tag",
            new=mock.AsyncMock(return_value=True),
        ) as mock_db_delete_tag,
    ):
        # Act
        await delete_tag(tag_id=tag_id, current_user=mock_user)

        # Assert
        mock_db_delete_tag.assert_called_once_with(tag_id)


@pytest.mark.asyncio
async def test_delete_tag_unauthorized():
    """Test tag deletion with unauthorized user (not admin)."""
    # Arrange
    tag_id = uuid.uuid4()

    # Create mock user with moderator role (not admin)
    mock_user = mock.MagicMock()
    mock_user.role = "moderator"

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await delete_tag(tag_id=tag_id, current_user=mock_user)

    # Verify the exception details
    assert excinfo.value.status_code == 403
    assert "Only admins can delete tags" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_tag_not_found():
    """Test tag deletion with non-existent tag."""
    # Arrange
    tag_id = uuid.uuid4()

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Mock dependencies to return None (tag not found)
    with mock.patch(
        "backend.routes.tags.delete_tag.get_tag_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_tag(tag_id=tag_id, current_user=mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Tag not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_tag_used_by_topics():
    """Test tag deletion when tag is used by topics."""
    # Arrange
    tag_id = uuid.uuid4()

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Create mock existing tag
    mock_existing_tag = mock.MagicMock()
    mock_existing_tag.id = tag_id
    mock_existing_tag.name = "Test Tag"
    mock_existing_tag.slug = "test-tag"

    # Create mock topics that use the tag
    mock_topics = [mock.MagicMock(), mock.MagicMock()]

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.tags.delete_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_existing_tag),
        ),
        mock.patch(
            "backend.routes.tags.delete_tag.get_topics_for_tag",
            new=mock.AsyncMock(return_value=mock_topics),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_tag(tag_id=tag_id, current_user=mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert "Cannot delete tag as it is used by 2 topics" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_tag_failure():
    """Test tag deletion with server failure."""
    # Arrange
    tag_id = uuid.uuid4()

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Create mock existing tag
    mock_existing_tag = mock.MagicMock()
    mock_existing_tag.id = tag_id
    mock_existing_tag.name = "Test Tag"
    mock_existing_tag.slug = "test-tag"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.tags.delete_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_existing_tag),
        ),
        mock.patch(
            "backend.routes.tags.delete_tag.get_topics_for_tag",
            new=mock.AsyncMock(return_value=[]),
        ),
        mock.patch(
            "backend.routes.tags.delete_tag.db_delete_tag",
            new=mock.AsyncMock(return_value=False),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_tag(tag_id=tag_id, current_user=mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 500
        assert "Failed to delete tag" in excinfo.value.detail
