# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db_functions.tags.create_tag import create_tag
from backend.schemas.tag import TagResponse


@pytest.fixture
def mock_tag() -> mock.MagicMock:
    tag = mock.MagicMock(spec=Tag)
    tag.id = uuid.uuid4()
    tag.name = "Test Tag"
    tag.slug = "test-tag"
    return tag


@pytest.fixture
def mock_tag_response(mock_tag) -> TagResponse:
    return mock.MagicMock(spec=TagResponse)


@pytest.mark.asyncio
async def test_create_tag_success(mock_tag, mock_tag_response) -> None:
    # Arrange
    name = "Test Tag"
    slug = "test-tag"

    # Mock the database query - RULE #10 compliance: only operates on Tag model
    with (
        mock.patch.object(
            Tag, "create", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_create,
        mock.patch(
            "backend.db_functions.tags.create_tag.tag_to_schema",
            new=mock.AsyncMock(return_value=mock_tag_response),
        ) as mock_converter,
    ):
        # Act
        result = await create_tag(name=name, slug=slug)

        # Assert
        assert result is not None
        assert result == mock_tag_response

        # Verify function calls
        mock_create.assert_called_once_with(name=name, slug=slug)
        mock_converter.assert_called_once_with(mock_tag)


@pytest.mark.asyncio
async def test_create_tag_duplicate_name() -> None:
    # Arrange
    name = "Test Tag"
    slug = "test-tag"
    db_error = IntegrityError("Duplicate name")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_tag(name=name, slug=slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(name=name, slug=slug)


@pytest.mark.asyncio
async def test_create_tag_duplicate_slug() -> None:
    # Arrange
    name = "New Tag"
    slug = "existing-slug"
    db_error = IntegrityError("Duplicate slug")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_tag(name=name, slug=slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(name=name, slug=slug)


@pytest.mark.asyncio
async def test_create_tag_database_error() -> None:
    # Arrange
    name = "Test Tag"
    slug = "test-tag"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "create", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_create:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await create_tag(name=name, slug=slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_create.assert_called_once_with(name=name, slug=slug)
