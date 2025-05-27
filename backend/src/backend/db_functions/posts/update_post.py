# Standard library imports
from typing import Optional
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostResponse


async def update_post(post_id: UUID, content: str) -> Optional[PostResponse]:
    post = await Post.get_or_none(id=post_id)
    if post:
        post.content = content
        await post.save()
        return await post_to_schema(post)
    return None
