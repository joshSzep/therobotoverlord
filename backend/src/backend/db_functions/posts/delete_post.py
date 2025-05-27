# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.post import Post


async def delete_post(post_id: UUID) -> bool:
    post = await Post.get_or_none(id=post_id)
    if post:
        await post.delete()
        return True
    return False
