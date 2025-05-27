# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.post import Post


async def get_reply_count(post_id: UUID) -> int:
    return await Post.filter(parent_post_id=post_id).count()
