# Standard library imports
from typing import Any
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

# Third-party imports
from dominate.tags import a
from dominate.tags import button
from dominate.tags import div
from dominate.tags import form
from dominate.tags import h1
from dominate.tags import h2
from dominate.tags import input_
from dominate.tags import label
from dominate.tags import p
from dominate.tags import span
from dominate.tags import textarea

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.pending_post import PendingPostResponse

# Project-specific imports
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


def render_post(
    post: Union[PostResponse, PendingPostResponse],
    topic_id: UUID,
    indent_level: int = 0,
    current_user: Optional[Any] = None,
    highlight_post_id: Optional[str] = None,
    is_pending: bool = False,
    is_admin: bool = False,
) -> None:
    """Recursively render a post and its replies."""
    # Add logging for debugging admin status
    import logging

    logger = logging.getLogger("backend")

    # Log the current admin status and user information
    user_name = current_user.display_name if current_user else None
    logger.info(
        f"Rendering post {post.id}, is_admin={is_admin}, current_user={user_name}"
    )

    # Log additional user details if available
    if current_user:
        logger.info(
            f"Current user ID: {current_user.id}, "
            f"display name: {current_user.display_name}"
        )

    # Add highlight class if this post is the one to highlight
    post_classes = f"post-container indent-level-{indent_level}"
    if highlight_post_id and str(post.id) == highlight_post_id:
        post_classes += " highlighted-post"

    # Add pending class if this is a pending post
    if is_pending:
        post_classes += " pending-post"

    with div(cls=post_classes, id=f"post-{post.id}"):  # type: ignore
        # Post header with author info
        with div(cls="post-header"), div(cls="post-meta"):  # type: ignore
            # Author info
            a(
                post.author.display_name,
                href=f"/html/profile/{post.author.id}/",
                cls="author-link",
            )  # type: ignore

            # Approval counts
            approved_count = getattr(post.author, "approved_count", 0)
            rejected_count = getattr(post.author, "rejected_count", 0)

            span(
                f"✓ {approved_count}",
                cls="approved",
            )  # type: ignore
            span(
                f"✗ {rejected_count}",
                cls="rejected",
            )  # type: ignore

            # Post content as a deep link
        with div(cls="post-content"):  # type: ignore
            # Make the full content a deep link back to this page with it highlighted
            post_url = f"/html/topics/{topic_id}/"
            post_url += f"?highlight={post.id}"

            # Add pending status indicator if this is a pending post
            if is_pending:
                with div(cls="pending-status"):  # type: ignore
                    span("AWAITING APPROVAL", cls="pending-badge")  # type: ignore

                    # Add moderation controls for admins or post owners
                    is_owner = False
                    if (
                        current_user
                        and hasattr(post, "author")
                        and hasattr(post.author, "id")
                    ):
                        is_owner = post.author.id == current_user.id
                    if is_admin or is_owner:
                        with div(cls="moderation-controls"):  # type: ignore
                            # Approval form
                            with form(
                                action=f"/html/pending-posts/{post.id}/moderate/",
                                method="post",
                                cls="inline-moderation-form",
                            ):  # type: ignore
                                input_(type="hidden", name="action", value="approve")  # type: ignore
                                button("APPROVE", type="submit", cls="approve-button")  # type: ignore

                            # Rejection form
                            with form(
                                action=f"/html/pending-posts/{post.id}/moderate/",
                                method="post",
                                cls="inline-moderation-form",
                            ):  # type: ignore
                                input_(type="hidden", name="action", value="reject")  # type: ignore
                                input_(
                                    type="text",
                                    name="moderation_reason",
                                    placeholder="Reason",
                                    cls="rejection-reason",
                                )  # type: ignore
                                button("REJECT", type="submit", cls="reject-button")  # type: ignore

                        # Debug info about admin status (will be removed in production)
                        with div(cls="debug-info"):  # type: ignore
                            span(
                                f"DEBUG - is_admin: {is_admin}",
                                style="color: red; font-weight: bold;",
                            )  # type: ignore

                        # AI Moderation button in its own div (only for admins)
                        if is_admin:
                            with (
                                div(cls="ai-moderation-controls"),  # type: ignore
                                form(  # type: ignore
                                    action=f"/html/pending-posts/{post.id}/trigger-ai-moderation/",
                                    method="post",
                                ),
                            ):
                                button(
                                    "⚙️ TRIGGER AI MODERATION ⚙️",
                                    type="submit",
                                    cls="ai-moderation-button",
                                )  # type: ignore

            # Use different styling for pending posts
            content_class = (
                "post-content-link pending-content"
                if is_pending
                else "post-content-link"
            )
            a(post.content, href=post_url, cls=content_class)  # type: ignore

        # Post metadata
        with div(cls="post-meta"):  # type: ignore
            # Format the datetime to string to avoid TypeError
            formatted_date = (
                post.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if post.created_at
                else "Unknown"
            )
            span(f"Posted: {formatted_date}")  # type: ignore

        # Reply button and form - only for approved posts
        if current_user and not is_pending:
            with div(cls="reply-actions"):  # type: ignore
                button(
                    "Reply",
                    cls="reply-toggle-btn",
                    onclick=f"toggleReplyForm('reply-form-{post.id}')",
                )  # type: ignore

            # Create reply form container
            with (
                div(
                    id=f"reply-form-{post.id}", cls="reply-form", style="display: none;"
                ),  # type: ignore
                form(action=f"/html/posts/{post.id}/reply/", method="post"),  # type: ignore
            ):
                # Include the topic_id for proper redirection
                input_(type="hidden", name="topic_id", value=str(topic_id))  # type: ignore
                with div(cls="form-group"):  # type: ignore
                    textarea(
                        name="content",
                        placeholder="Write your reply...",
                        cls="form-control",
                    )  # type: ignore
                button("Submit Reply", type="submit", cls="btn btn-primary")  # type: ignore

        # Render replies recursively (only for approved posts since pending posts
        # don't have replies.) Pending posts can be replies to approved posts, but
        # they don't have their own replies yet
        if (
            not is_pending
            and hasattr(post, "replies")
            and getattr(post, "replies", None)
        ):
            with div(cls="replies"):  # type: ignore
                # Use getattr to safely access replies
                replies = getattr(post, "replies", [])
                for reply in replies:
                    # Check if this reply is a pending post
                    is_reply_pending = isinstance(reply, PendingPostResponse)

                    render_post(
                        reply,
                        topic_id=topic_id,
                        indent_level=indent_level + 1,
                        current_user=current_user,
                        highlight_post_id=highlight_post_id,
                        is_pending=is_reply_pending,
                        is_admin=is_admin,
                    )


def create_topic_detail_page(
    topic: TopicResponse,
    posts: List[PostResponse],
    total_posts: int,
    current_page: int,
    total_pages: int,
    current_user: Optional[UserResponse] = None,
    highlight_post_id: Optional[str] = None,
    pending_posts: Optional[List[PendingPostResponse]] = None,
    is_admin: bool = False,
) -> str:
    """
    Create the topic detail page using Dominate.

    Args:
        topic: Topic schema object
        posts: List of post schema objects
        total_posts: Total number of posts
        current_page: Current page number
        total_pages: Total number of pages
        current_user: Optional user schema object
        pagination: Pagination information
        user: Optional user schema object

    Returns:
        A dominate document object
    """
    # Define the content function to be passed to the base document

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Topic detail section
        with div(cls="topic-detail"):  # type: ignore
            # Make the title a deep link back to this page with no highlight
            with h1():  # type: ignore
                a(topic.title, href=f"/html/topics/{topic.id}/", cls="topic-title-link")  # type: ignore

            topic_desc = getattr(topic, "description", "")
            p(topic_desc, cls="topic-description")  # type: ignore

            # Topic tags
            tags = getattr(topic, "tags", [])
            if tags:
                with div(cls="topic-tags"):  # type: ignore
                    for tag in tags:
                        a(
                            tag.name,
                            href=f"/html/tags/{tag.slug}/",
                            cls="tag",
                        )  # type: ignore

        # Posts section
        with div(cls="topic-posts"), div(cls="posts-section"):  # type: ignore
            if posts or (pending_posts and current_user):
                # Add CSS for threaded posts
                with div(cls="threaded-posts"):  # type: ignore
                    # Render all posts - both approved and pending (if user is logged
                    # in.) Create a list to hold all posts (both approved and pending)
                    all_posts: List[Union[PostResponse, PendingPostResponse]] = []

                    # Add approved posts
                    for post in posts:
                        all_posts.append(post)

                    # Add pending posts if user is logged in
                    if pending_posts and current_user:
                        for pending_post in pending_posts:
                            all_posts.append(pending_post)

                    # Sort all posts by creation date (newest first)
                    all_posts.sort(key=lambda p: p.created_at, reverse=True)

                    # Render each post recursively
                    for post_item in all_posts:
                        # Check if this is a pending post
                        is_post_pending = isinstance(post_item, PendingPostResponse)

                        render_post(
                            post_item,
                            topic_id=topic.id,
                            indent_level=0,
                            current_user=current_user,
                            highlight_post_id=highlight_post_id,
                            is_pending=is_post_pending,
                            is_admin=is_admin,
                        )

                # Pagination controls
                with div(cls="pagination"):  # type: ignore
                    if current_page > 1:
                        prev_url = f"/html/topics/{topic.id}/?page={current_page - 1}"
                        a("Previous", href=prev_url)  # type: ignore

                    page_text = f"Page {current_page} of {total_pages}"
                    span(page_text)  # type: ignore

                    if current_page < total_pages:
                        next_url = f"/html/topics/{topic.id}/?page={current_page + 1}"
                        a("Next", href=next_url)  # type: ignore
            else:
                p("NO POSTS HAVE BEEN APPROVED FOR THIS TOPIC")  # type: ignore

        # Create post form section (only if user is logged in)
        if current_user:
            with div(cls="create-post"):  # type: ignore
                h2("SUBMIT NEW POST")  # type: ignore
                with form(
                    action="/html/posts/",
                    method="post",
                    cls="post-submission-form",
                ):  # type: ignore
                    input_(type="hidden", name="topic_id", value=topic.id)  # type: ignore

                    with div(cls="form-group content-group"):  # type: ignore
                        label("YOUR STATEMENT:", for_="content", cls="content-label")  # type: ignore
                        textarea(
                            id="content",
                            name="content",
                            rows="6",
                            required=True,
                            cls="content-textarea",
                            placeholder="ENTER YOUR LOGICAL CONTRIBUTION HERE...",
                        )  # type: ignore

                    button(
                        "SUBMIT FOR APPROVAL",
                        type="submit",
                        cls="submit-button",
                    )  # type: ignore

    # Create the base document with the content function
    result: str = create_base_document(
        title_text=f"{topic.title} - The Robot Overlord",
        user=current_user,
        content_func=content_func,
    )
    return result
