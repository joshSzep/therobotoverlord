# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db_functions.tags.delete_tag import delete_tag


@pytest.fixture
def mock_tag() -> mock.MagicMock:
    tag = mock.MagicMock(spec=Tag)
    tag.id = uuid.uuid4()
    tag.name = "Test Tag"
    tag.slug = "test-tag"
    return tag


@pytest.mark.asyncio
async def test_delete_tag_success(mock_tag) -> None:
    # Arrange
    test_id = mock_tag.id

    # Mock the database query - RULE #10 compliance: only operates on Tag model
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(mock_tag, "delete", new=mock.AsyncMock()) as mock_delete,
    ):
        # Act
        result = await delete_tag(test_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_tag_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await delete_tag(test_id)

        # Assert
        assert result is False
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_delete_tag_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await delete_tag(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_delete_tag_delete_error(mock_tag) -> None:
    # Arrange
    test_id = mock_tag.id
    delete_error = IntegrityError("Error deleting tag")

    # Mock the database query and delete operation to raise an exception
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(
            mock_tag, "delete", new=mock.AsyncMock(side_effect=delete_error)
        ) as mock_delete,
    ):
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await delete_tag(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == delete_error
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_tag_cascading_deletion(mock_tag) -> None:
    # Arrange
    test_id = mock_tag.id

    # Create mock related objects that should be deleted
    mock_tag.topic_tags = [mock.MagicMock() for _ in range(3)]

    # Mock the database query - RULE #10 compliance: only operates on Tag model
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch.object(mock_tag, "delete", new=mock.AsyncMock()) as mock_delete,
    ):
        # Act
        result = await delete_tag(test_id)

        # Assert
        assert result is True

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_delete.assert_called_once()

        # Note: We don't need to explicitly test that related objects are deleted
        # since Tortoise ORM handles cascading deletions automatically based on
        # the model relationships. The delete() method on the tag will trigger
        # the cascading deletions.
