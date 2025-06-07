# Standard library imports
from typing import Any
from typing import List
from typing import Optional
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

# Project-specific imports
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


def render_post(
    post: PostResponse,
    topic_id: UUID,
    indent_level: int = 0,
    current_user: Optional[Any] = None,
    highlight_post_id: Optional[str] = None,
) -> None:
    """Recursively render a post and its replies."""
    # Add highlight class if this post is the one to highlight
    post_classes = f"post-container indent-level-{indent_level}"
    if highlight_post_id and str(post.id) == highlight_post_id:
        post_classes += " highlighted-post"

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
            a(post.content, href=post_url, cls="post-content-link")  # type: ignore

        # Post metadata
        with div(cls="post-meta"):  # type: ignore
            # Format the datetime to string to avoid TypeError
            formatted_date = (
                post.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if post.created_at
                else "Unknown"
            )
            span(f"Posted: {formatted_date}")  # type: ignore

        # Reply button and form
        if current_user:
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
                form(action="/html/posts/reply/", method="post"),  # type: ignore
            ):
                # Use the topic_id passed from the parent topic
                input_(type="hidden", name="topic_id", value=str(topic_id))  # type: ignore
                input_(type="hidden", name="parent_post_id", value=str(post.id))  # type: ignore
                with div(cls="form-group"):  # type: ignore
                    textarea(
                        name="content",
                        placeholder="Write your reply...",
                        cls="form-control",
                    )  # type: ignore
                button("Submit Reply", type="submit", cls="btn btn-primary")  # type: ignore

        # Render replies if any exist
        if hasattr(post, "replies") and post.replies:
            with div(cls="replies"):  # type: ignore
                for reply in post.replies:
                    render_post(
                        reply,
                        topic_id,
                        indent_level + 1,
                        current_user,
                        highlight_post_id=highlight_post_id,
                    )


def create_topic_detail_page(
    topic: TopicResponse,
    posts: List[PostResponse],
    total_posts: int,
    current_page: int,
    total_pages: int,
    current_user: Optional[UserResponse] = None,
    highlight_post_id: Optional[str] = None,
) -> Any:
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
                        span(tag.name, cls="tag")  # type: ignore

        # Posts section
        with div(cls="topic-posts"):  # type: ignore
            h2("APPROVED POSTS")  # type: ignore

            if posts:
                # Add CSS for threaded posts
                with div(cls="threaded-posts"):  # type: ignore
                    # Render each post recursively
                    for post in posts:
                        render_post(
                            post,
                            topic_id=topic.id,
                            indent_level=0,
                            current_user=current_user,
                            highlight_post_id=highlight_post_id,
                        )

                # Pagination controls
                with div(cls="pagination"):  # type: ignore
                    if current_page > 1:
                        a(
                            "Previous",
                            href=f"/html/topics/{topic.id}/?page={current_page - 1}",
                        )  # type: ignore

                    span(f"Page {current_page} of {total_pages}")  # type: ignore

                    if current_page < total_pages:
                        a(
                            "Next",
                            href=f"/html/topics/{topic.id}/?page={current_page + 1}",
                        )  # type: ignore
            else:
                p("NO POSTS HAVE BEEN APPROVED FOR THIS TOPIC")  # type: ignore

        # Create post form section (only if user is logged in)
        if current_user:
            with div(cls="create-post"):  # type: ignore
                h2("SUBMIT NEW POST")  # type: ignore
                with form(action="/html/posts/", method="post"):  # type: ignore
                    input_(type="hidden", name="topic_id", value=topic.id)  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        label("Title:", for_="title")  # type: ignore
                        input_(type="text", id="title", name="title", required=True)  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        label("Content:", for_="content")  # type: ignore
                        textarea(id="content", name="content", rows="6", required=True)  # type: ignore

                    button("SUBMIT FOR APPROVAL", type="submit")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text=f"{topic.title} - The Robot Overlord",
        user=current_user,
        content_func=content_func,
    )
