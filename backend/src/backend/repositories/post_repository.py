# Standard library imports
from typing import Optional
from typing import Union
from uuid import UUID

# Project-specific imports
from backend.converters import post_to_schema
from backend.db.models.post import Post
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse


class PostRepository:
    @staticmethod
    async def list_posts(
        skip: int = 0,
        limit: int = 20,
        topic_id: Optional[UUID] = None,
        author_id: Optional[UUID] = None,
    ) -> PostList:
        # Build query with filters
        query = Post.all()

        if topic_id:
            query = query.filter(topic_id=topic_id)

        if author_id:
            query = query.filter(author_id=author_id)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        posts = await query.offset(skip).limit(limit)

        # Convert ORM models to schema objects using async converter
        post_responses: list[PostResponse] = []
        for post in posts:
            post_responses.append(await post_to_schema(post))

        return PostList(posts=post_responses, count=count)

    @staticmethod
    async def get_post_by_id(post_id: UUID) -> Optional[PostResponse]:
        post = await Post.get_or_none(id=post_id)
        if post:
            return await post_to_schema(post)
        return None

    @staticmethod
    async def create_post(
        content: str,
        author_id: UUID,
        topic_id: UUID,
        parent_post_id: Optional[UUID] = None,
    ) -> PostResponse:
        post_data: dict[str, Union[str, UUID, Optional[UUID]]] = {
            "content": content,
            "author_id": author_id,
            "topic_id": topic_id,
        }

        if parent_post_id:
            post_data["parent_post_id"] = parent_post_id

        post = await Post.create(using_db=None, **post_data)
        return await post_to_schema(post)

    @staticmethod
    async def update_post(post_id: UUID, content: str) -> Optional[PostResponse]:
        post = await Post.get_or_none(id=post_id)
        if post:
            post.content = content
            await post.save()
            return await post_to_schema(post)
        return None

    @staticmethod
    async def delete_post(post_id: UUID) -> bool:
        post = await Post.get_or_none(id=post_id)
        if post:
            await post.delete()
            return True
        return False

    @staticmethod
    async def is_user_post_author(post_id: UUID, user_id: UUID) -> bool:
        post = await Post.get_or_none(id=post_id)
        if not post:
            return False

        await post.fetch_related("author")
        return str(post.author.id) == str(user_id)

    @staticmethod
    async def get_reply_count(post_id: UUID) -> int:
        return await Post.filter(parent_post_id=post_id).count()

    @staticmethod
    async def list_post_replies(
        post_id: UUID, skip: int = 0, limit: int = 20
    ) -> PostList:
        query = Post.filter(parent_post_id=post_id)

        # Get total count for pagination
        count = await query.count()

        # Apply pagination
        replies = await query.offset(skip).limit(limit)

        # Convert ORM models to schema objects using async converter
        reply_responses: list[PostResponse] = []
        for reply in replies:
            reply_responses.append(await post_to_schema(reply))

        return PostList(posts=reply_responses, count=count)
