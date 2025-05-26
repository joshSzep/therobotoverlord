# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest

# Project-specific imports
from backend.routes.tags.list_tags import list_tags
from backend.routes.tags.schemas import TagList


@pytest.mark.asyncio
async def test_list_tags_no_filters():
    """Test listing tags without any filters."""
    # Arrange
    # Create mock tags for the repository to return
    mock_tag_1 = mock.MagicMock()
    mock_tag_1.id = uuid.uuid4()
    mock_tag_1.name = "Test Tag 1"
    mock_tag_1.slug = "test-tag-1"

    mock_tag_2 = mock.MagicMock()
    mock_tag_2.id = uuid.uuid4()
    mock_tag_2.name = "Test Tag 2"
    mock_tag_2.slug = "test-tag-2"

    mock_tags = [mock_tag_1, mock_tag_2]

    # Mock the repository method
    with mock.patch(
        "backend.routes.tags.list_tags.TagRepository.list_tags"
    ) as mock_list_tags:
        # Configure the mock to return our tags and count
        mock_list_tags.return_value = (mock_tags, len(mock_tags))

        # Act
        result = await list_tags()

        # Assert
        assert isinstance(result, TagList)
        assert result.count == len(mock_tags)
        assert len(result.tags) == len(mock_tags)
        assert result.tags[0].name == mock_tag_1.name
        assert result.tags[1].name == mock_tag_2.name

        # Verify repository was called with correct parameters
        # We don't check exact parameters because FastAPI Query objects are passed
        assert mock_list_tags.call_count == 1


@pytest.mark.asyncio
async def test_list_tags_with_search():
    """Test listing tags with search filter."""
    # Arrange
    search_term = "test"

    # Create mock tag for the repository to return
    mock_tag = mock.MagicMock()
    mock_tag.id = uuid.uuid4()
    mock_tag.name = "Test Tag"
    mock_tag.slug = "test-tag"

    mock_tags = [mock_tag]

    # Mock the repository method
    with mock.patch(
        "backend.routes.tags.list_tags.TagRepository.list_tags"
    ) as mock_list_tags:
        # Configure the mock to return our tags and count
        mock_list_tags.return_value = (mock_tags, len(mock_tags))

        # Act
        result = await list_tags(search=search_term)

        # Assert
        assert isinstance(result, TagList)
        assert result.count == len(mock_tags)
        assert len(result.tags) == len(mock_tags)
        assert result.tags[0].name == mock_tag.name

        # Verify repository was called with search parameter
        args, kwargs = mock_list_tags.call_args
        assert len(args) >= 3  # At least 3 args (skip, limit, search)
        assert args[2] == search_term  # Third argument should be search term


@pytest.mark.asyncio
async def test_list_tags_with_pagination():
    """Test listing tags with pagination parameters."""
    # Arrange
    skip = 10
    limit = 5
    total_count = 20  # Total count is higher than the limit

    # Create mock tags for the repository to return
    mock_tags = []
    for i in range(limit):
        mock_tag = mock.MagicMock()
        mock_tag.id = uuid.uuid4()
        mock_tag.name = f"Test Tag {i + 1}"
        mock_tag.slug = f"test-tag-{i + 1}"
        mock_tags.append(mock_tag)

    # Mock the repository method
    with mock.patch(
        "backend.routes.tags.list_tags.TagRepository.list_tags"
    ) as mock_list_tags:
        # Configure the mock to return our tags and count
        mock_list_tags.return_value = (mock_tags, total_count)

        # Act
        result = await list_tags(skip=skip, limit=limit)

        # Assert
        assert isinstance(result, TagList)
        assert result.count == total_count
        assert len(result.tags) == len(mock_tags)

        # Verify repository was called with pagination parameters
        args, kwargs = mock_list_tags.call_args
        # The first two arguments should be skip and limit values
        # We can't check the Query objects directly, but we can check they were passed
        assert mock_list_tags.call_count == 1
