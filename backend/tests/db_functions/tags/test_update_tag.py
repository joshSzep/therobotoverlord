# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db_functions.tags.update_tag import update_tag
from backend.schemas.tag import TagResponse


@pytest.fixture
def mock_tag() -> mock.MagicMock:
    tag = mock.MagicMock(spec=Tag)
    tag.id = uuid.uuid4()
    tag.name = "Original Tag"
    tag.slug = "original-tag"
    return tag


@pytest.fixture
def mock_tag_response(mock_tag) -> TagResponse:
    return mock.MagicMock(spec=TagResponse)


@pytest.mark.asyncio
async def test_update_tag_success(mock_tag, mock_tag_response) -> None:
    # Arrange
    test_id = mock_tag.id
    new_name = "Updated Tag"
    new_slug = "updated-tag"

    # Mock the database query - RULE #10 compliance: only operates on Tag model
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(mock_tag, "save", new=mock.AsyncMock()) as mock_save,
        mock.patch(
            "backend.db_functions.tags.update_tag.tag_to_schema",
            new=mock.AsyncMock(return_value=mock_tag_response),
        ) as mock_converter,
    ):
        # Act
        result = await update_tag(tag_id=test_id, name=new_name, slug=new_slug)

        # Assert
        assert result is not None
        assert result == mock_tag_response
        assert mock_tag.name == new_name
        assert mock_tag.slug == new_slug

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
        mock_converter.assert_called_once_with(mock_tag)


@pytest.mark.asyncio
async def test_update_tag_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_name = "Updated Tag"
    new_slug = "updated-tag"

    # Mock the database query
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await update_tag(tag_id=test_id, name=new_name, slug=new_slug)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_tag_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    new_name = "Updated Tag"
    new_slug = "updated-tag"
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_tag(tag_id=test_id, name=new_name, slug=new_slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_update_tag_save_error(mock_tag) -> None:
    # Arrange
    test_id = mock_tag.id
    new_name = "Updated Tag"
    new_slug = "updated-tag"
    save_error = IntegrityError("Error saving tag")

    # Mock the database query and save operation to raise an exception
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(
            mock_tag, "save", new=mock.AsyncMock(side_effect=save_error)
        ) as mock_save,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_tag(tag_id=test_id, name=new_name, slug=new_slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_update_tag_duplicate_name(mock_tag) -> None:
    # Arrange
    test_id = mock_tag.id
    new_name = "Existing Tag"  # Name that already exists for another tag
    new_slug = "updated-tag"
    save_error = IntegrityError("Duplicate name")

    # Mock the database query and save operation to raise an exception
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(
            mock_tag, "save", new=mock.AsyncMock(side_effect=save_error)
        ) as mock_save,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_tag(tag_id=test_id, name=new_name, slug=new_slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_update_tag_duplicate_slug(mock_tag) -> None:
    # Arrange
    test_id = mock_tag.id
    new_name = "Updated Tag"
    new_slug = "existing-slug"  # Slug that already exists for another tag
    save_error = IntegrityError("Duplicate slug")

    # Mock the database query and save operation to raise an exception
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(
            mock_tag, "save", new=mock.AsyncMock(side_effect=save_error)
        ) as mock_save,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await update_tag(tag_id=test_id, name=new_name, slug=new_slug)

        # Verify the exception is propagated correctly
        assert exc_info.value == save_error
        mock_get.assert_called_once_with(id=test_id)
        mock_save.assert_called_once()
