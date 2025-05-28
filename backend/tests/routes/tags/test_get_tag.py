# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.tags.get_tag import get_tag


@pytest.mark.asyncio
async def test_get_tag_success():
    """Test successful tag retrieval."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Test Tag"
    tag_slug = "test-tag"

    # Create mock tag response
    mock_tag = mock.MagicMock()
    mock_tag.id = tag_id
    mock_tag.name = tag_name
    mock_tag.slug = tag_slug

    # Mock dependencies
    with mock.patch(
        "backend.routes.tags.get_tag.get_tag_by_id",
        new=mock.AsyncMock(return_value=mock_tag),
    ) as mock_get_tag_by_id:
        # Act
        result = await get_tag(tag_id=tag_id)

        # Assert
        assert result == mock_tag
        mock_get_tag_by_id.assert_called_once_with(tag_id)


@pytest.mark.asyncio
async def test_get_tag_not_found():
    """Test tag retrieval with non-existent tag."""
    # Arrange
    tag_id = uuid.uuid4()

    # Mock dependencies to return None (tag not found)
    with mock.patch(
        "backend.routes.tags.get_tag.get_tag_by_id",
        new=mock.AsyncMock(return_value=None),
    ) as mock_get_tag_by_id:
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_tag(tag_id=tag_id)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Tag not found" in excinfo.value.detail
        mock_get_tag_by_id.assert_called_once_with(tag_id)
