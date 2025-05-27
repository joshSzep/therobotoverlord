# Standard library imports
from uuid import UUID

# Project-specific imports
from backend.db.models.post import Post


async def is_user_post_author(post_id: UUID, user_id: UUID) -> bool:
    post = await Post.get_or_none(id=post_id)
    if not post:
        return False

    await post.fetch_related("author")
    return str(post.author.id) == str(user_id)
