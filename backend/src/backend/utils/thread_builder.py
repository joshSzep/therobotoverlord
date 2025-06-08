"""
Thread structure builder for combining approved and pending posts.
"""

import logging
from typing import Dict
from typing import List
from typing import Set
from uuid import UUID

from backend.schemas.pending_post import PendingPostResponse
from backend.schemas.post import PostResponse
from backend.schemas.post_lookup import PostType
from backend.schemas.post_lookup import ThreadPost

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def convert_to_thread_post(post: PostResponse) -> ThreadPost:
    """Convert a PostResponse to a ThreadPost."""
    return ThreadPost(
        id=post.id,
        content=post.content,
        author_id=post.author.id,
        parent_post_id=getattr(post, "parent_post_id", None),
        replies=[],
        post_type=PostType.APPROVED,
        original_post=post,
    )


def convert_pending_to_thread_post(pending_post: PendingPostResponse) -> ThreadPost:
    """Convert a PendingPostResponse to a ThreadPost."""
    return ThreadPost(
        id=pending_post.id,
        content=pending_post.content,
        author_id=pending_post.author.id,
        parent_post_id=pending_post.parent_post_id,
        replies=[],
        post_type=PostType.PENDING,
        original_post=pending_post,
    )


def build_thread_structure(
    posts: List[PostResponse],
    pending_posts: List[PendingPostResponse],
    current_user_id: UUID,
) -> List[ThreadPost]:
    """
    Build a unified thread structure including both approved and pending posts.

    Args:
        posts: List of approved posts
        pending_posts: List of pending posts
        current_user_id: Current user ID for permission checking

    Returns:
        A list of top-level ThreadPost objects with nested replies
    """
    # Create mappings for posts and their replies
    post_map: Dict[str, ThreadPost] = {}
    reply_map: Dict[str, List[ThreadPost]] = {}
    top_level_posts: List[ThreadPost] = []

    # Track which posts we've processed to avoid duplicates
    processed_ids: Set[str] = set()

    # Process approved posts first
    for post in posts:
        post_id = str(post.id)
        if post_id in processed_ids:
            continue

        # Convert to ThreadPost
        thread_post = convert_to_thread_post(post)
        post_map[post_id] = thread_post
        processed_ids.add(post_id)

        # If this is a top-level post (no parent), add to top_level_posts
        if not thread_post.parent_post_id:
            top_level_posts.append(thread_post)
        else:
            # This is a reply, track it in the reply_map
            parent_id = str(thread_post.parent_post_id)
            if parent_id not in reply_map:
                reply_map[parent_id] = []
            reply_map[parent_id].append(thread_post)

        # Process any existing replies in the post
        if hasattr(post, "replies") and post.replies:
            for reply in post.replies:
                reply_id = str(reply.id)
                if reply_id in processed_ids:
                    continue

                thread_reply = convert_to_thread_post(reply)
                post_map[reply_id] = thread_reply
                processed_ids.add(reply_id)

                # Add to reply map
                parent_id = (
                    str(thread_reply.parent_post_id)
                    if thread_reply.parent_post_id
                    else post_id
                )
                if parent_id not in reply_map:
                    reply_map[parent_id] = []
                reply_map[parent_id].append(thread_reply)

    # Process pending posts
    logger.info(f"Processing {len(pending_posts)} pending posts")
    pending_included = 0
    pending_excluded_not_author = 0
    pending_excluded_duplicate = 0

    for pending_post in pending_posts:
        # Log details about this pending post
        logger.info(
            f"Evaluating pending post {pending_post.id}: "
            f"author={pending_post.author.id}, "
            f"parent_id={pending_post.parent_post_id}"
        )

        # Only include pending posts that belong to the current user
        if str(pending_post.author.id) != str(current_user_id):
            logger.info(
                f"Excluding post {pending_post.id}: wrong author. "
                f"(author={pending_post.author.id}, user={current_user_id})"
            )
            pending_excluded_not_author += 1
            continue

        pending_id = str(pending_post.id)
        if pending_id in processed_ids:
            logger.info(f"Excluding pending post {pending_post.id}: already processed")
            pending_excluded_duplicate += 1
            continue

        # Convert to ThreadPost
        thread_post = convert_pending_to_thread_post(pending_post)
        post_map[pending_id] = thread_post
        processed_ids.add(pending_id)
        pending_included += 1

        # If this is a top-level post (no parent), add to top_level_posts
        if not thread_post.parent_post_id:
            top_level_posts.append(thread_post)
            logger.info(f"Added pending post {pending_post.id} as top-level post")
        else:
            # This is a reply, track it in the reply_map
            parent_id = str(thread_post.parent_post_id)
            if parent_id not in reply_map:
                reply_map[parent_id] = []
            reply_map[parent_id].append(thread_post)

            # Check if parent exists in the current view
            if parent_id in post_map:
                logger.info(
                    f"Added pending post {pending_post.id} as reply to "
                    f"visible parent {parent_id}"
                )
            else:
                logger.info(
                    f"Added pending post {pending_post.id} as reply to "
                    f"parent {parent_id} which is NOT in the current view"
                )

    # Attach replies to their parent posts
    replies_attached = 0
    orphaned_replies = 0
    for post_id, replies in reply_map.items():
        if post_id not in post_map:
            logger.info(
                f"Parent {post_id} not in view, orphaning {len(replies)} replies"
            )
            orphaned_replies += len(replies)
            continue

        parent_post = post_map[post_id]
        parent_post.replies.extend(replies)
        replies_attached += len(replies)

    # Log summary statistics
    logger.info(
        f"Thread building summary: {len(top_level_posts)} top-level posts, "
        f"{pending_included} pending posts included, "
        f"{pending_excluded_not_author} excluded (not author), "
        f"{pending_excluded_duplicate} excluded (duplicate), "
        f"{replies_attached} replies attached, "
        f"{orphaned_replies} orphaned replies"
    )

    return top_level_posts
