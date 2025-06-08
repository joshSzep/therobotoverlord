# Standard library imports
import logging
from typing import Annotated
from typing import Any
from typing import List
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.db_functions.posts.enhance_posts_with_topics_for_profile import (
    enhance_posts_with_topics_for_profile,
)
from backend.db_functions.posts.list_pending_posts_by_user import (
    list_pending_posts_by_user,
)
from backend.db_functions.posts.list_posts_by_user import list_posts_by_user
from backend.db_functions.users.get_user_by_id import get_user_by_id
from backend.dominate_templates.profile.index import create_profile_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional
from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.post import PostResponse

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()


def convert_pending_to_post_response(pending: PendingPostResponse) -> PostResponse:
    """Convert a PendingPostResponse to a PostResponse for template compatibility."""
    # Create a PostResponse with the common fields from PendingPostResponse
    return PostResponse(
        id=pending.id,
        author=pending.author,
        topic_id=pending.topic_id,
        parent_post_id=pending.parent_post_id,
        created_at=pending.created_at,
        updated_at=pending.updated_at,
        content=pending.content,
        reply_count=0,  # Pending posts don't have replies
        replies=[],  # Empty list for replies
    )


@router.get("/{user_id}/", response_class=HTMLResponse)
async def get_user_profile(
    request: Request,
    user_id: UUID,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    post_page: int = Query(1, ge=1),
    post_limit: int = Query(5, ge=1, le=20),
) -> HTMLResponse:
    # Get the requested user
    try:
        user_schema = await get_user_by_id(user_id)
        if not user_schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        # Convert UserSchema to UserResponse
        profile_user = UserResponse(
            id=user_schema.id,
            email=user_schema.email,
            display_name=user_schema.display_name,
            is_verified=user_schema.is_verified,
            last_login=user_schema.last_login,
            role=user_schema.role,
            is_locked=user_schema.is_locked,
            created_at=user_schema.created_at,
            updated_at=user_schema.updated_at,
            approved_count=user_schema.approved_count,
            rejected_count=user_schema.rejected_count,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get user's posts with pagination
    post_offset = (post_page - 1) * post_limit
    user_posts_result = await list_posts_by_user(
        user_id,
        limit=post_limit,
        offset=post_offset,
        count_only=False,
    )
    user_posts = user_posts_result if isinstance(user_posts_result, list) else []

    # Get total count for pagination
    total_post_count = await list_posts_by_user(user_id, count_only=True)
    # Use ternary operator to handle type checking
    post_count = total_post_count if isinstance(total_post_count, int) else 0
    total_post_pages = (post_count + post_limit - 1) // post_limit

    # Create pagination data for posts
    post_pagination = {
        "current_page": post_page,
        "total_pages": total_post_pages,
        "has_previous": post_page > 1,
        "has_next": post_page < total_post_pages,
        "previous_page": post_page - 1,
        "next_page": post_page + 1,
    }

    # Get user's pending posts (only if viewing own profile)
    pending_posts = []
    if current_user and current_user.id == user_id:
        # Increase limit to make sure we get all pending posts
        pending_posts = await list_pending_posts_by_user(user_id, limit=20)
        logger.info(f"Found {len(pending_posts)} pending posts for user {user_id}")

    # Fetch topic information for all posts
    # We need to handle both PostResponse and PendingPostResponse types
    # Since they share common fields like topic_id, we can use them with
    # enhance_posts_with_topics_for_profile
    all_posts: List[Any] = []
    if user_posts:
        all_posts.extend(user_posts)
    if pending_posts:
        all_posts.extend(pending_posts)
    topic_map = await enhance_posts_with_topics_for_profile(all_posts)

    # Convert pending posts to post responses for template compatibility
    converted_pending_posts = None
    if pending_posts:
        converted_pending_posts = [
            convert_pending_to_post_response(p) for p in pending_posts
        ]
        logger.info(
            f"Converted {len(converted_pending_posts)} pending posts to PostResponse"
        )

    # Create the profile page using Dominate
    doc = create_profile_page(
        profile_user=profile_user,
        current_user=current_user,
        user_posts=user_posts,
        pending_posts=converted_pending_posts,
        post_pagination=post_pagination,
        topic_map=topic_map,
        is_own_profile=bool(current_user and current_user.id == user_id),
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
