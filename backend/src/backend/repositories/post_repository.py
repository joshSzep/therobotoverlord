# Standard library imports
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from uuid import UUID

# Project-specific imports
from backend.db.models.post import Post


class PostRepository:
    @staticmethod
    async def list_posts(
        skip: int = 0,
        limit: int = 20,
        topic_id: Optional[UUID] = None,
        author_id: Optional[UUID] = None,
    ) -> Tuple[List[Post], int]:
        # Build query with filters
        query = Post.all().prefetch_related("author", "topic")

        if topic_id:
            query = query.filter(topic_id=topic_id)

        if author_id:
            query = query.filter(author_id=author_id)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        posts = await query.offset(skip).limit(limit)

        return posts, count

    @staticmethod
    async def get_post_by_id(post_id: UUID) -> Optional[Post]:
        return await Post.get_or_none(id=post_id).prefetch_related("author", "topic")

    @staticmethod
    async def create_post(
        content: str,
        author_id: UUID,
        topic_id: UUID,
        parent_post_id: Optional[UUID] = None,
    ) -> Post:
        post_data: dict[str, Union[str, UUID, Optional[UUID]]] = {
            "content": content,
            "author_id": author_id,
            "topic_id": topic_id,
        }

        if parent_post_id:
            post_data["parent_post_id"] = parent_post_id

        return await Post.create(using_db=None, **post_data)

    @staticmethod
    async def update_post(post_id: UUID, content: str) -> Optional[Post]:
        post = await Post.get_or_none(id=post_id)
        if post:
            post.content = content
            await post.save()
            await post.fetch_related("author", "topic")
        return post

    @staticmethod
    async def delete_post(post_id: UUID) -> bool:
        post = await Post.get_or_none(id=post_id)
        if post:
            await post.delete()
            return True
        return False

    @staticmethod
    async def get_reply_count(post_id: UUID) -> int:
        return await Post.filter(parent_post_id=post_id).count()

    @staticmethod
    async def list_post_replies(
        post_id: UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Post], int]:
        query = Post.filter(parent_post_id=post_id).prefetch_related("author", "topic")

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        replies = await query.offset(skip).limit(limit)

        return replies, count
