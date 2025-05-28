# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.topics.add_topic_tag import AddTagRequest
from backend.routes.topics.add_topic_tag import add_topic_tag
from backend.schemas.tag import TagResponse


@pytest.mark.asyncio
async def test_add_topic_tag_success():
    """Test successful tag addition to a topic."""
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = uuid.uuid4()

    # Create mock topic and tag
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    mock_tag = mock.MagicMock()
    mock_tag.id = tag_id
    mock_tag.name = "Test Tag"
    mock_tag.slug = "test-tag"

    # Create request
    request = AddTagRequest(tag_id=tag_id)

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_topic_tag",
            new=mock.AsyncMock(return_value=None),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.create_topic_tag",
            new=mock.AsyncMock(),
        ) as mock_create_topic_tag,
    ):
        # Act
        result = await add_topic_tag(
            topic_id=topic_id,
            request=request,
            current_user=mock_user,
        )

        # Assert
        assert isinstance(result, TagResponse)
        assert result.id == tag_id
        assert result.name == "Test Tag"
        assert result.slug == "test-tag"

        # Verify function calls
        mock_create_topic_tag.assert_called_once_with(topic_id, tag_id)


@pytest.mark.asyncio
async def test_add_topic_tag_topic_not_found():
    """Test tag addition with non-existent topic."""
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = uuid.uuid4()

    # Create request
    request = AddTagRequest(tag_id=tag_id)

    # Mock dependencies - simulate topic not found
    with mock.patch(
        "backend.routes.topics.add_topic_tag.get_topic_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await add_topic_tag(
                topic_id=topic_id,
                request=request,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Topic not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_add_topic_tag_tag_not_found():
    """Test tag addition with non-existent tag."""
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = uuid.uuid4()

    # Create mock topic
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    # Create request
    request = AddTagRequest(tag_id=tag_id)

    # Mock dependencies - simulate tag not found
    with (
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=None),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await add_topic_tag(
                topic_id=topic_id,
                request=request,
                current_user=mock_user,
            )

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Tag not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_add_topic_tag_already_exists():
    """Test tag addition when tag is already associated with the topic."""
    # Arrange
    topic_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = uuid.uuid4()

    # Create mock topic, tag, and topic_tag
    mock_topic = mock.MagicMock()
    mock_topic.id = topic_id

    mock_tag = mock.MagicMock()
    mock_tag.id = tag_id
    mock_tag.name = "Test Tag"
    mock_tag.slug = "test-tag"

    mock_topic_tag = mock.MagicMock()
    mock_topic_tag.topic_id = topic_id
    mock_topic_tag.tag_id = tag_id

    # Create request
    request = AddTagRequest(tag_id=tag_id)

    # Mock dependencies - simulate tag already associated
    with (
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_topic_by_id",
            new=mock.AsyncMock(return_value=mock_topic),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_tag_by_id",
            new=mock.AsyncMock(return_value=mock_tag),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.get_topic_tag",
            new=mock.AsyncMock(return_value=mock_topic_tag),
        ),
        mock.patch(
            "backend.routes.topics.add_topic_tag.create_topic_tag",
            new=mock.AsyncMock(),
        ) as mock_create_topic_tag,
    ):
        # Act
        result = await add_topic_tag(
            topic_id=topic_id,
            request=request,
            current_user=mock_user,
        )

        # Assert
        assert isinstance(result, TagResponse)
        assert result.id == tag_id
        assert result.name == "Test Tag"
        assert result.slug == "test-tag"

        # Verify function calls - create_topic_tag should not be called
        mock_create_topic_tag.assert_not_called()
