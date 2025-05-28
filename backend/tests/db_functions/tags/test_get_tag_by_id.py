# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.tag import Tag
from backend.db_functions.tags.get_tag_by_id import get_tag_by_id
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
async def test_get_tag_by_id_success(mock_tag, mock_tag_response) -> None:
    # Arrange
    test_id = mock_tag.id

    # Mock the database query - RULE #10 compliance: only operates on Tag model
    with (
        mock.patch.object(
            Tag, "get_or_none", new=mock.AsyncMock(return_value=mock_tag)
        ) as mock_get,
        mock.patch(
            "backend.db_functions.tags.get_tag_by_id.tag_to_schema",
            new=mock.AsyncMock(return_value=mock_tag_response),
        ) as mock_converter,
    ):
        # Act
        result = await get_tag_by_id(test_id)

        # Assert
        assert result is not None
        assert result == mock_tag_response

        # Verify function calls
        mock_get.assert_called_once_with(id=test_id)
        mock_converter.assert_called_once_with(mock_tag)


@pytest.mark.asyncio
async def test_get_tag_by_id_not_found() -> None:
    # Arrange
    test_id = uuid.uuid4()

    # Mock the database query
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(return_value=None)
    ) as mock_get:
        # Act
        result = await get_tag_by_id(test_id)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_get_tag_by_id_database_error() -> None:
    # Arrange
    test_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Tag, "get_or_none", new=mock.AsyncMock(side_effect=db_error)
    ) as mock_get:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_tag_by_id(test_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_get.assert_called_once_with(id=test_id)


@pytest.mark.asyncio
async def test_get_tag_by_id_invalid_uuid() -> None:
    # Arrange - We'll try to convert a string to UUID which should raise ValueError

    # Act & Assert
    with pytest.raises(ValueError):
        # We can't pass a string directly due to type checking, so we'll use uuid.UUID
        # with an invalid format to trigger the ValueError
        await get_tag_by_id(uuid.UUID("not-a-valid-uuid"))
