# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import IntegrityError

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.posts.get_reply_count import get_reply_count


@pytest.mark.asyncio
async def test_get_reply_count_success() -> None:
    # Arrange
    post_id = uuid.uuid4()
    expected_count = 5

    # Mock the database query - RULE #10 compliance: only operates on Post model
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
    ):
        # Act
        result = await get_reply_count(post_id=post_id)

        # Assert
        assert result == expected_count

        # Verify function calls
        mock_filter.assert_called_once_with(parent_post_id=post_id)
        mock_count.assert_called_once()


@pytest.mark.asyncio
async def test_get_reply_count_no_replies() -> None:
    # Arrange
    post_id = uuid.uuid4()
    expected_count = 0

    # Mock the database query
    with (
        mock.patch.object(Post, "filter", return_value=mock.MagicMock()) as mock_filter,
        mock.patch.object(
            mock_filter.return_value,
            "count",
            new=mock.AsyncMock(return_value=expected_count),
        ) as mock_count,
    ):
        # Act
        result = await get_reply_count(post_id=post_id)

        # Assert
        assert result == expected_count

        # Verify function calls
        mock_filter.assert_called_once_with(parent_post_id=post_id)
        mock_count.assert_called_once()


@pytest.mark.asyncio
async def test_get_reply_count_database_error() -> None:
    # Arrange
    post_id = uuid.uuid4()
    db_error = IntegrityError("Database connection error")

    # Mock the database query to raise an exception
    with mock.patch.object(
        Post, "filter", new=mock.MagicMock(side_effect=db_error)
    ) as mock_filter:
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await get_reply_count(post_id=post_id)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_filter.assert_called_once_with(parent_post_id=post_id)
