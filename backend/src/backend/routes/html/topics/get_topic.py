# Standard library imports
import logging
from typing import Annotated
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

# Project-specific imports
from backend.db.models.post import Post
from backend.db_functions.pending_posts.list_pending_posts_by_topic_and_user import (
    list_pending_posts_by_topic_and_user,
)
from backend.db_functions.posts.find_post_from_pending_post import (
    find_post_from_pending_post,
)
from backend.db_functions.posts.get_post_by_id import get_post_by_id
from backend.db_functions.posts.list_threaded_posts_by_topic import (
    list_threaded_posts_by_topic,
)
from backend.db_functions.topics import get_topic_by_id
from backend.dominate_templates.topics.detail import create_topic_detail_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional
from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.post import PostResponse
from backend.schemas.rejected_post import RejectedPostResponse
from backend.utils.post_lookup import find_post_by_id
from backend.utils.thread_builder import build_thread_structure

# Set up logger
logger = logging.getLogger(__name__)


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


router = APIRouter()


@router.get("/{topic_id}/", response_class=HTMLResponse)
async def get_topic_page(
    request: Request,
    topic_id: UUID,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    highlight: Optional[str] = Query(None, description="Post ID to highlight"),
) -> Response:  # Changed to Response to allow for RedirectResponse
    # Get topic
    topic = await get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get posts for this topic with pagination
    skip = (page - 1) * limit
    posts_data = await list_threaded_posts_by_topic(topic_id, skip=skip, limit=limit)

    # Extract posts and total count
    posts = posts_data.posts
    total_count = posts_data.count
    total_pages = (total_count + limit - 1) // limit

    # Debug logging for posts
    logger.debug(f"Retrieved {len(posts)} posts for topic {topic_id}")

    # Get pending posts for this topic if user is logged in
    pending_posts: List[PendingPostResponse] = []
    # Initialize thread_posts and top_level_pending_posts
    thread_posts = []
    top_level_pending_posts: List[PendingPostResponse] = []

    if current_user:
        # Get pending posts for this user
        # Admin-specific features will be implemented in a future update

        # For now, all users (including admins) only see their own pending posts
        # This is a temporary simplification until we implement the full admin view
        pending_posts = await list_pending_posts_by_topic_and_user(
            topic_id=topic_id, user_id=current_user.id
        )

        # Log all pending posts to help with debugging
        logger.info(
            f"Retrieved {len(pending_posts)} pending posts for topic {topic_id} "
            f"and user {current_user.id}"
        )

        # Log details of each pending post
        for i, pp in enumerate(pending_posts):
            logger.info(
                f"Pending post {i + 1}/{len(pending_posts)}: "
                f"id={pp.id}, parent_id={pp.parent_post_id}, "
                f"author={pp.author.id}, content={pp.content[:30]}..."
            )

        # If we have a highlight, check if it's in the pending posts
        if highlight:
            logger.info(f"Looking for highlight {highlight} in pending posts")
            for pp in pending_posts:
                if str(pp.id) == highlight:
                    logger.info(f"Found highlight {highlight} in pending posts!")
                    break

        # Use our thread builder utility to create a unified thread structure
        # with both approved and pending posts
        thread_posts = build_thread_structure(
            posts=posts, pending_posts=pending_posts, current_user_id=current_user.id
        )

        # Log the thread structure
        logger.debug(f"Built thread structure with {len(thread_posts)} top-level posts")

        # Extract ALL pending posts for template compatibility, not just top-level ones
        # This is needed because the template still expects a separate list of pending
        # posts. Clear the existing list before populating it.
        top_level_pending_posts.clear()

        # First, add all pending posts directly from our pending_posts list
        # This ensures we include ALL pending posts regardless of thread structure
        for pending_post in pending_posts:
            if pending_post.author.id == current_user.id:
                top_level_pending_posts.append(pending_post)
                logger.info(f"Added pending post {pending_post.id} to display list")

        logger.info(
            f"Added {len(top_level_pending_posts)} pending posts to display list "
            f"out of {len(pending_posts)} total pending posts"
        )

        logger.debug(f"Found {len(top_level_pending_posts)} top-level pending posts")

        # For template compatibility, we need to ensure all posts have their replies
        # properly sorted. This is handled by the thread builder, but we log it here
        # for consistency.
        logger.debug("Thread posts have been sorted by creation date")

    # Log the structure of posts before rendering
    logger.info(f"Number of approved posts to render: {len(posts)}")
    for i, post in enumerate(posts):
        has_replies = hasattr(post, "replies") and getattr(post, "replies", None)
        num_replies = len(getattr(post, "replies", [])) if has_replies else 0
        logger.info(
            f"Post {i}: id={post.id}, has_replies={has_replies}, "
            f"num_replies={num_replies}"
        )

    logger.info(f"Top-level pending posts: {len(top_level_pending_posts)}")

    # Check if the highlight parameter is a UUID
    highlight_uuid = None
    if highlight:
        try:
            highlight_uuid = UUID(highlight)
        except ValueError:
            logger.warning(f"Invalid highlight UUID: {highlight}")

    # Use our post lookup utility to find the post regardless of its status
    highlight_exists = False
    if highlight_uuid and current_user:
        # Try to find the post using our unified lookup utility
        post_lookup_result = await find_post_by_id(
            post_id=highlight_uuid,
            current_user_id=current_user.id if current_user else None,
        )

        if post_lookup_result:
            # We found the post
            post_type = post_lookup_result.type
            # We don't need to use the post object directly, just check if it's visible
            # Type annotation is just for mypy
            _: Union[PostResponse, PendingPostResponse, RejectedPostResponse] = (
                post_lookup_result.post
            )
            visible_to_user = post_lookup_result.visible_to_user

            logger.info(
                f"Found post with ID {highlight_uuid} of type {post_type.value}, "
                f"visible to user: {visible_to_user}"
            )

            # If the post is visible to the user, we don't need to redirect
            if visible_to_user:
                highlight_exists = True
                logger.info(
                    f"Post {highlight_uuid} is visible to user, no redirection needed"
                )
            else:
                logger.info(
                    f"Post {highlight_uuid} exists but is not visible to current user"
                )
        else:
            logger.info(f"Post {highlight_uuid} not found in any status")

    # If we still need to check if the post is in the current view (for highlighting)
    if highlight_uuid and highlight_exists:
        # Check if the post is in the current view (for highlighting purposes)
        in_current_view = False

        # Check in thread posts (which includes both approved and pending posts)
        for thread_post in thread_posts:
            if str(thread_post.id) == highlight:
                in_current_view = True
                logger.info(
                    f"Found highlighted post in top-level thread posts: {highlight}"
                )
                break

            # Check in nested replies
            for reply in thread_post.replies:
                if str(reply.id) == highlight:
                    in_current_view = True
                    logger.info(
                        f"Found highlighted post in nested replies: {highlight}"
                    )
                    break
            if in_current_view:
                break

        if not in_current_view:
            logger.info(
                f"Post {highlight_uuid} exists but is not in the current view (pagination)"  # noqa: E501
            )
            # We could potentially redirect to a different page here in the future

    # Only perform redirection if the highlighted post doesn't exist or isn't visible
    # to the user
    if highlight_uuid and not highlight_exists:
        # Try to find the approved post using our user event tracking system
        approved_post = await find_post_from_pending_post(highlight_uuid)

        if approved_post:
            # We found the approved post that corresponds to the pending post
            logger.info(
                f"Found approved post {approved_post.id} that replaced "
                f"pending post {highlight_uuid} via event tracking"
            )
            return RedirectResponse(
                f"/html/topics/{topic_id}/?highlight={str(approved_post.id)}",
                status_code=302,
            )
        else:
            # No direct link found via events, log this for debugging
            logger.debug(
                f"No event tracking found for pending post {highlight_uuid}, "
                "falling back to heuristic search"
            )

            # As a fallback, we can still use the old heuristic approach
            # Look for recent posts in this topic
            recent_posts = (
                await Post.filter(topic_id=topic_id).order_by("-created_at").limit(20)
            )

            # Try to find a matching post by checking if it's in our current view
            for db_post in recent_posts:
                # Get the post as a PostResponse to maintain type compatibility
                post_response = await get_post_by_id(db_post.id)
                if not post_response:
                    continue

                for view_post in posts:
                    if str(view_post.id) == str(post_response.id):
                        logger.info(
                            f"Found approved post {post_response.id} that may replace "
                            f"pending post {highlight_uuid} via heuristic"
                        )
                        return RedirectResponse(
                            f"/html/topics/{topic_id}/?highlight={str(post_response.id)}",
                            status_code=302,
                        )

    # Create the topic detail page using Dominate
    doc = create_topic_detail_page(
        topic=topic,
        posts=posts,
        pending_posts=top_level_pending_posts,  # Pass pending posts directly
        total_posts=total_count,
        total_pages=total_pages,
        current_page=page,
        current_user=current_user,
        highlight_post_id=highlight,
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
