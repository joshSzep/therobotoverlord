# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.posts.delete_post import delete_post


@pytest.mark.asyncio
async def test_delete_post_success():
    """Test successful post deletion."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create mock user (author)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Post content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.delete_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.is_user_post_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.db_delete_post",
            new=mock.AsyncMock(return_value=True),
        ) as mock_db_delete_post,
    ):
        # Act
        await delete_post(post_id=post_id, current_user=mock_user)
        
        # Assert
        mock_db_delete_post.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_as_admin():
    """Test successful post deletion by admin (not author)."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create mock user (admin)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "admin"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Post content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.delete_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.is_user_post_author",
            new=mock.AsyncMock(return_value=False),  # Not the author
        ),
        mock.patch(
            "backend.routes.posts.delete_post.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.db_delete_post",
            new=mock.AsyncMock(return_value=True),
        ) as mock_db_delete_post,
    ):
        # Act
        await delete_post(post_id=post_id, current_user=mock_user)
        
        # Assert
        mock_db_delete_post.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_not_found():
    """Test post deletion with non-existent post."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Mock dependencies to return None (post not found)
    with mock.patch(
        "backend.routes.posts.delete_post.get_post_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_post(post_id=post_id, current_user=mock_user)
        
        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Post not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_post_unauthorized():
    """Test post deletion with unauthorized user (not author or admin)."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create mock user (not author or admin)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Post content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.delete_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.is_user_post_author",
            new=mock.AsyncMock(return_value=False),  # Not the author
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_post(post_id=post_id, current_user=mock_user)
        
        # Verify the exception details
        assert excinfo.value.status_code == 403
        assert "You don't have permission to delete this post" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_post_with_replies():
    """Test post deletion when post has replies."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    reply_count = 5
    
    # Create mock user (author)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Post content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.delete_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.is_user_post_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.get_reply_count",
            new=mock.AsyncMock(return_value=reply_count),
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_post(post_id=post_id, current_user=mock_user)
        
        # Verify the exception details
        assert excinfo.value.status_code == 400
        error_msg = f"Cannot delete post as it has {reply_count} replies"
        assert error_msg in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_post_failure():
    """Test post deletion with deletion failure."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create mock user (author)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Post content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.delete_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.is_user_post_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.get_reply_count",
            new=mock.AsyncMock(return_value=0),
        ),
        mock.patch(
            "backend.routes.posts.delete_post.db_delete_post",
            new=mock.AsyncMock(return_value=False),  # Deletion failed
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await delete_post(post_id=post_id, current_user=mock_user)
        
        # Verify the exception details
        assert excinfo.value.status_code == 500
        assert "Failed to delete post" in excinfo.value.detail
