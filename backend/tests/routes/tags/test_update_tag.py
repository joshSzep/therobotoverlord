# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest
from slugify import slugify
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.routes.tags.update_tag import update_tag


@pytest.mark.asyncio
async def test_update_tag_success():
    """Test successful tag update."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Updated Tag"
    tag_slug = slugify(tag_name)

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Create mock existing tag
    mock_existing_tag = mock.MagicMock()
    mock_existing_tag.id = tag_id
    mock_existing_tag.name = "Original Tag"
    mock_existing_tag.slug = "original-tag"

    # Create mock updated tag
    mock_updated_tag = mock.MagicMock()
    mock_updated_tag.id = tag_id
    mock_updated_tag.name = tag_name
    mock_updated_tag.slug = tag_slug

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.tags.update_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_existing_tag),
        ),
        mock.patch(
            "backend.routes.tags.update_tag.db_update_tag",
            new=mock.AsyncMock(return_value=mock_updated_tag),
        ) as mock_db_update_tag,
    ):
        # Act
        result = await update_tag(
            tag_id=tag_id, tag_data=tag_data, current_user=mock_user
        )

        # Assert
        assert result == mock_updated_tag
        mock_db_update_tag.assert_called_once_with(
            tag_id=tag_id,
            name=tag_name,
            slug=tag_slug,
        )


@pytest.mark.asyncio
async def test_update_tag_unauthorized():
    """Test tag update with unauthorized user (not admin or moderator)."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Updated Tag"

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with regular user role
    mock_user = mock.MagicMock()
    mock_user.role = "user"

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await update_tag(tag_id=tag_id, tag_data=tag_data, current_user=mock_user)

    # Verify the exception details
    assert excinfo.value.status_code == 403
    assert "Only moderators and admins can update tags" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_tag_not_found():
    """Test tag update with non-existent tag."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Updated Tag"

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Mock dependencies to return None (tag not found)
    with mock.patch(
        "backend.routes.tags.update_tag.get_tag_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_tag(tag_id=tag_id, tag_data=tag_data, current_user=mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Tag not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_tag_duplicate_name():
    """Test tag update with a name that already exists."""
    # Arrange
    tag_id = uuid.uuid4()
    tag_name = "Existing Tag"

    # Create mock tag data
    tag_data = mock.MagicMock()
    tag_data.name = tag_name

    # Create mock user with admin role
    mock_user = mock.MagicMock()
    mock_user.role = "admin"

    # Create mock existing tag
    mock_existing_tag = mock.MagicMock()
    mock_existing_tag.id = tag_id
    mock_existing_tag.name = "Original Tag"
    mock_existing_tag.slug = "original-tag"

    # Mock dependencies to simulate IntegrityError
    with (
        mock.patch(
            "backend.routes.tags.update_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_existing_tag),
        ),
        mock.patch(
            "backend.routes.tags.update_tag.db_update_tag",
            new=mock.AsyncMock(side_effect=IntegrityError("Tag already exists")),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_tag(tag_id=tag_id, tag_data=tag_data, current_user=mock_user)

        # Verify the exception details
        assert excinfo.value.status_code == 409
        assert "A tag with this name already exists" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_tag_as_moderator():
    """Test successful tag update by a moderator."""
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

    # Create mock existing tag
    mock_existing_tag = mock.MagicMock()
    mock_existing_tag.id = tag_id
    mock_existing_tag.name = "Original Tag"
    mock_existing_tag.slug = "original-tag"

    # Create mock updated tag
    mock_updated_tag = mock.MagicMock()
    mock_updated_tag.id = tag_id
    mock_updated_tag.name = tag_name
    mock_updated_tag.slug = tag_slug

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.tags.update_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_existing_tag),
        ),
        mock.patch(
            "backend.routes.tags.update_tag.db_update_tag",
            new=mock.AsyncMock(return_value=mock_updated_tag),
        ) as mock_db_update_tag,
    ):
        # Act
        result = await update_tag(
            tag_id=tag_id, tag_data=tag_data, current_user=mock_user
        )

        # Assert
        assert result == mock_updated_tag
        mock_db_update_tag.assert_called_once_with(
            tag_id=tag_id,
            name=tag_name,
            slug=tag_slug,
        )
