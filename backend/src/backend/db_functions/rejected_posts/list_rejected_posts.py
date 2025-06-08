from typing import List
from typing import Optional
from uuid import UUID

from backend.converters.rejected_post_to_schema import rejected_post_to_schema
from backend.db.models.rejected_post import RejectedPost
from backend.schemas.rejected_post import RejectedPostList
from backend.schemas.rejected_post import RejectedPostResponse


async def list_rejected_posts(
    user_id: Optional[UUID] = None,
    limit: int = 10,
    offset: int = 0,
) -> RejectedPostList:
    """
    List rejected posts with pagination.

    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of results to return
        offset: Number of results to skip

    Returns:
        RejectedPostList: List of rejected posts with pagination metadata
    """
    query = RejectedPost.all()

    if user_id:
        query = query.filter(user_id=user_id)

    count = await query.count()

    rejected_posts = await query.order_by("-created_at").offset(offset).limit(limit)

    rejected_post_responses: List[RejectedPostResponse] = [
        await rejected_post_to_schema(rejected_post) for rejected_post in rejected_posts
    ]

    return RejectedPostList(
        rejected_posts=rejected_post_responses,
        count=count,
    )
