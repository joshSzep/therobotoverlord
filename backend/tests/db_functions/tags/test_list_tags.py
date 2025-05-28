# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db_functions.tags.list_tags import list_tags
from backend.schemas.tag import TagList
from backend.schemas.tag import TagResponse


@pytest.fixture
def mock_tags() -> list[mock.MagicMock]:
    tags = []
    for i in range(3):
        tag = mock.MagicMock(spec=Tag)
        tag.id = uuid.uuid4()
        tag.name = f"Test Tag {i}"
        tag.slug = f"test-tag-{i}"
        tags.append(tag)
    return tags


@pytest.fixture
def mock_tag_responses(mock_tags) -> list[TagResponse]:
    return [mock.MagicMock(spec=TagResponse) for _ in mock_tags]


@pytest.mark.asyncio
async def test_list_tags_success(mock_tags, mock_tag_responses) -> None:
    # Arrange
    skip = 0
    limit = 50
    expected_count = len(mock_tags)

    # Mock the database query - RULE #10 compliance: only operates on Tag model
    with (
        mock.patch.object(Tag, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_tags),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.tags.list_tags.tag_to_schema",
            new=mock.AsyncMock(side_effect=mock_tag_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_tags(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, TagList)
        assert result.count == expected_count
        assert len(result.tags) == expected_count
        assert result.tags == mock_tag_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_tags_with_search(mock_tags, mock_tag_responses) -> None:
    # Arrange
    skip = 0
    limit = 50
    search = "test"
    expected_count = len(mock_tags)

    # Mock the database query
    with (
        mock.patch.object(Tag, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value, "filter", return_value=mock.MagicMock()
        ) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_filter.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_tags),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.tags.list_tags.tag_to_schema",
            new=mock.AsyncMock(side_effect=mock_tag_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_tags(skip=skip, limit=limit, search=search)

        # Assert
        assert result is not None
        assert isinstance(result, TagList)
        assert result.count == expected_count
        assert len(result.tags) == expected_count
        assert result.tags == mock_tag_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_filter.assert_called_once_with(name__icontains=search)
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_tags_with_pagination(mock_tags, mock_tag_responses) -> None:
    # Arrange
    skip = 5
    limit = 10
    expected_count = len(mock_tags)

    # Mock the database query
    with (
        mock.patch.object(Tag, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=mock_tags),
        ) as mock_limit,
        mock.patch(
            "backend.db_functions.tags.list_tags.tag_to_schema",
            new=mock.AsyncMock(side_effect=mock_tag_responses),
        ) as mock_converter,
    ):
        # Act
        result = await list_tags(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, TagList)
        assert result.count == expected_count
        assert len(result.tags) == expected_count
        assert result.tags == mock_tag_responses

        # Verify function calls
        mock_all.assert_called_once()
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)
        assert mock_converter.call_count == expected_count


@pytest.mark.asyncio
async def test_list_tags_empty_results() -> None:
    # Arrange
    skip = 0
    limit = 50
    expected_count = 0
    empty_tags = []

    # Mock the database query
    with (
        mock.patch.object(Tag, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch.object(
            mock_all.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
        mock.patch.object(
            mock_all.return_value, "offset", return_value=mock.MagicMock()
        ) as mock_offset,
        mock.patch.object(
            mock_offset.return_value,
            "limit",
            new=mock.AsyncMock(return_value=empty_tags),
        ) as mock_limit,
    ):
        # Act
        result = await list_tags(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert isinstance(result, TagList)
        assert result.count == expected_count
        assert len(result.tags) == expected_count

        # Verify function calls
        mock_all.assert_called_once()
        mock_count.assert_called_once()
        mock_offset.assert_called_once_with(skip)
        mock_limit.assert_called_once_with(limit)


@pytest.mark.asyncio
async def test_list_tags_database_error() -> None:
    # Arrange
    skip = 0
    limit = 50
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "all", new=mock.MagicMock(side_effect=db_error)
    ) as mock_all:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await list_tags(skip=skip, limit=limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_all.assert_called_once()
