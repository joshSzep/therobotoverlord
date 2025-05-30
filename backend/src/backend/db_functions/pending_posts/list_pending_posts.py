from typing import Optional
from uuid import UUID

from tortoise.expressions import Q

from backend.converters.pending_post_to_schema import pending_post_to_schema
from backend.db.models.pending_post import PendingPost
from backend.schemas.pending_post import PendingPostList
from backend.schemas.pending_post import PendingPostResponse


async def list_pending_posts(
    user_id: Optional[UUID] = None,
    topic_id: Optional[UUID] = None,
    limit: int = 10,
    offset: int = 0,
) -> PendingPostList:
    filters = Q()

    if user_id:
        filters &= Q(author_id=user_id)

    if topic_id:
        filters &= Q(topic_id=topic_id)

    total_count = await PendingPost.filter(filters).count()

    pending_posts = (
        await PendingPost.filter(filters)
        .limit(limit)
        .offset(offset)
        .order_by("-created_at")
    )

    pending_post_schemas: list[PendingPostResponse] = []
    for pending_post in pending_posts:
        pending_post_schemas.append(await pending_post_to_schema(pending_post))

    return PendingPostList(
        pending_posts=pending_post_schemas,
        count=total_count,
    )
