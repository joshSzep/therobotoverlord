# Standard library imports
from typing import Optional
from typing import Union
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


async def create_post(
    content: str,
    author_id: UUID,
    topic_id: UUID,
    parent_post_id: Optional[UUID] = None,
) -> PostResponse:
    """
    Create a new post.

    Args:
        content: The content of the post
        author_id: The UUID of the post author
        topic_id: The UUID of the topic this post belongs to
        parent_post_id: Optional UUID of the parent post if this is a reply

    Returns:
        PostResponse representing the newly created post
    """
    post_data: dict[str, Union[str, UUID, Optional[UUID]]] = {
        "content": content,
        "author_id": author_id,
        "topic_id": topic_id,
    }

    if parent_post_id:
        post_data["parent_post_id"] = parent_post_id

    post = await Post.create(using_db=None, **post_data)
    return await post_to_schema(post)
