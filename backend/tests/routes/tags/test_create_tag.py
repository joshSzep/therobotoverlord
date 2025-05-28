# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest
from slugify import slugify
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.routes.tags.create_tag import create_tag


@pytest.mark.asyncio
async def test_create_tag_success():
    """Test successful tag creation."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Test Tag"
    tag_slug = slugify(tag_name)

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Create mock response
    mock_tag_response = mock.MagicMock()
    mock_tag_response.id = tag_id
    mock_tag_response.name = tag_name
    mock_tag_response.slug = tag_slug

    # Mock dependencies
    with mock.patch(
        "backend.routes.tags.create_tag.db_create_tag",
        new=mock.AsyncMock(return_value=mock_tag_response),
    ) as mock_db_create_tag:
        # Act
        result = await create_tag(tag_data=tag_data, current_user=mock_user)

        # Assert
        assert result == mock_tag_response
        mock_db_create_tag.assert_called_once_with(
            name=tag_name,
            slug=tag_slug,
        )


@pytest.mark.asyncio
async def test_create_tag_unauthorized():
    """Test tag creation with unauthorized user (not admin or moderator)."""
    # Arrange
    tag_name = "Test Tag"

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with regular user role
    mock_user = mock.MagicMock()
    mock_user.role = "user"

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await create_tag(tag_data=tag_data, current_user=mock_user)

    # Verify the exception details
    assert excinfo.value.status_code == 403
    assert "Only moderators and admins can create tags" in excinfo.value.detail


@pytest.mark.asyncio
async def test_create_tag_duplicate_name():
    """Test tag creation with a name that already exists."""
    # Arrange
    tag_name = "Existing Tag"

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Mock dependencies to simulate IntegrityError
    with mock.patch(
        "backend.routes.tags.create_tag.db_create_tag",
        new=mock.AsyncMock(side_effect=IntegrityError("Tag already exists")),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await create_tag(tag_data=tag_data, current_user=mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 409
        assert "A tag with this name already exists" in excinfo.value.detail


@pytest.mark.asyncio
async def test_create_tag_as_moderator():
    """Test successful tag creation by a moderator."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Moderator Tag"
    tag_slug = slugify(tag_name)

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with moderator role
    mock_user = mock.MagicMock()
    mock_user.role = "moderator"

    # Create mock response
    mock_tag_response = mock.MagicMock()
    mock_tag_response.id = tag_id
    mock_tag_response.name = tag_name
    mock_tag_response.slug = tag_slug

    # Mock dependencies
    with mock.patch(
        "backend.routes.tags.create_tag.db_create_tag",
        new=mock.AsyncMock(return_value=mock_tag_response),
    ) as mock_db_create_tag:
        # Act
        result = await create_tag(tag_data=tag_data, current_user=mock_user)

        # Assert
        assert result == mock_tag_response
        mock_db_create_tag.assert_called_once_with(
            name=tag_name,
            slug=tag_slug,
        )
