# Standard library imports
from unittest import mock
import uuid

# Third-party imports
from fastapi import HTTPException
import pytest

# Project-specific imports
from backend.routes.posts.update_post import update_post


@pytest.mark.asyncio
async def test_update_post_success():
    """Test successful post update."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    new_content = "Updated post content"
    
    # Create mock post data
    post_data = mock.MagicMock()
    post_data.content = new_content
    
    # Create mock user (author)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Original content"
    
    # Create mock updated post
    mock_updated_post = mock.MagicMock()
    mock_updated_post.id = post_id
    mock_updated_post.content = new_content
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.update_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.update_post.is_user_post_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.posts.update_post.db_update_post",
            new=mock.AsyncMock(return_value=mock_updated_post),
        ) as mock_db_update_post,
    ):
        # Act
        result = await update_post(
            post_id=post_id,
            post_data=post_data,
            current_user=mock_user,
        )
        
        # Assert
        assert result == mock_updated_post
        mock_db_update_post.assert_called_once_with(post_id, new_content)


@pytest.mark.asyncio
async def test_update_post_as_admin():
    """Test successful post update by admin (not author)."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    new_content = "Admin updated content"
    
    # Create mock post data
    post_data = mock.MagicMock()
    post_data.content = new_content
    
    # Create mock user (admin)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "admin"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Original content"
    
    # Create mock updated post
    mock_updated_post = mock.MagicMock()
    mock_updated_post.id = post_id
    mock_updated_post.content = new_content
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.update_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.update_post.is_user_post_author",
            new=mock.AsyncMock(return_value=False),  # Not the author
        ),
        mock.patch(
            "backend.routes.posts.update_post.db_update_post",
            new=mock.AsyncMock(return_value=mock_updated_post),
        ) as mock_db_update_post,
    ):
        # Act
        result = await update_post(
            post_id=post_id,
            post_data=post_data,
            current_user=mock_user,
        )
        
        # Assert
        assert result == mock_updated_post
        mock_db_update_post.assert_called_once_with(post_id, new_content)


@pytest.mark.asyncio
async def test_update_post_not_found():
    """Test post update with non-existent post."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    new_content = "Updated post content"
    
    # Create mock post data
    post_data = mock.MagicMock()
    post_data.content = new_content
    
    # Create mock user
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Mock dependencies to return None (post not found)
    with mock.patch(
        "backend.routes.posts.update_post.get_post_by_id",
        new=mock.AsyncMock(return_value=None),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_post(
                post_id=post_id,
                post_data=post_data,
                current_user=mock_user,
            )
        
        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Post not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_post_unauthorized():
    """Test post update with unauthorized user (not author or admin)."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    new_content = "Updated post content"
    
    # Create mock post data
    post_data = mock.MagicMock()
    post_data.content = new_content
    
    # Create mock user (not author or admin)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Original content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.update_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.update_post.is_user_post_author",
            new=mock.AsyncMock(return_value=False),  # Not the author
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_post(
                post_id=post_id,
                post_data=post_data,
                current_user=mock_user,
            )
        
        # Verify the exception details
        assert excinfo.value.status_code == 403
        assert "You don't have permission to update this post" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_post_failure():
    """Test post update with update failure."""
    # Arrange
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    new_content = "Updated post content"
    
    # Create mock post data
    post_data = mock.MagicMock()
    post_data.content = new_content
    
    # Create mock user (author)
    mock_user = mock.MagicMock()
    mock_user.id = user_id
    mock_user.role = "user"
    
    # Create mock existing post
    mock_existing_post = mock.MagicMock()
    mock_existing_post.id = post_id
    mock_existing_post.content = "Original content"
    
    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.posts.update_post.get_post_by_id",
            new=mock.AsyncMock(return_value=mock_existing_post),
        ),
        mock.patch(
            "backend.routes.posts.update_post.is_user_post_author",
            new=mock.AsyncMock(return_value=True),
        ),
        mock.patch(
            "backend.routes.posts.update_post.db_update_post",
            new=mock.AsyncMock(return_value=None),  # Update failed
        ),
    ):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await update_post(
                post_id=post_id,
                post_data=post_data,
                current_user=mock_user,
            )
        
        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "Failed to update post" in excinfo.value.detail
