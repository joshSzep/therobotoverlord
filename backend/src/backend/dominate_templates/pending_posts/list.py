# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third-party imports
from dominate.tags import a
from dominate.tags import button
from dominate.tags import div
from dominate.tags import form
from dominate.tags import h1
from dominate.tags import h2
from dominate.tags import input_
from dominate.tags import p
from dominate.tags import span
from dominate.util import text

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.pending_post import PendingPostResponse


def create_pending_posts_list_page(
    pending_posts: List[PendingPostResponse],
    pagination: Dict[str, Any],
    user: Optional[UserResponse] = None,
    is_admin: bool = False,
    messages: Optional[List[Dict[str, str]]] = None,
) -> Any:
    """
    Create the pending posts list page using Dominate.

    Args:
        pending_posts: List of PendingPostResponse objects
        pagination: Pagination information
        user: UserResponse object
        is_admin: Whether the current user is an admin
        messages: List of message dictionaries

    Returns:
        A dominate document object
    """

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Display page title
        h1("PENDING POSTS AWAITING APPROVAL")  # type: ignore[no-untyped-call]

        if pending_posts:
            with div(cls="pending-posts-list"):  # type: ignore
                for pending_post in pending_posts:
                    with div(cls="pending-post-card"):  # type: ignore
                        # Post header with title
                        with div(cls="pending-post-header"), h2():  # type: ignore
                            a(
                                pending_post.title or "Untitled Post",
                                href=f"/html/pending-posts/{pending_post.id}/",
                                cls="pending-post-title-link",
                            )  # type: ignore[no-untyped-call]

                        # Post content section
                        with div(cls="pending-post-content"):  # type: ignore
                            # Content
                            if pending_post.content:
                                with div(cls="pending-post-content-text"):  # type: ignore
                                    p(pending_post.content)  # type: ignore

                            # Post metadata section
                            with div(cls="pending-post-meta"):  # type: ignore
                                # Topic info
                                with div(cls="pending-post-topic"):  # type: ignore
                                    if (
                                        hasattr(pending_post, "topic")
                                        and pending_post.topic
                                    ):
                                        text("Topic: ")  # type: ignore
                                        # Get topic title and id safely
                                        topic_title = pending_post.topic.get(
                                            "title", "Unknown"
                                        )
                                        topic_id = pending_post.topic.get(
                                            "id", pending_post.topic_id
                                        )
                                        a(
                                            topic_title,
                                            href=f"/html/topics/{topic_id}/",
                                            cls="topic-link",
                                        )  # type: ignore[no-untyped-call]
                                    else:
                                        span("No topic", cls="no-topic")  # type: ignore

                                # Author info
                                with div(cls="pending-post-author"):  # type: ignore
                                    text("Submitted by: ")  # type: ignore
                                    if (
                                        hasattr(pending_post, "user")
                                        and pending_post.user
                                    ):
                                        author_name = getattr(
                                            pending_post.user,
                                            "display_name",
                                            "Unknown",
                                        )
                                        author_id = getattr(
                                            pending_post.user,
                                            "id",
                                            None,
                                        )
                                        if author_id:
                                            href = f"/html/profile/{author_id}/"
                                            a(author_name, href=href)  # type: ignore
                                        else:
                                            text(author_name)  # type: ignore
                                    else:
                                        text("Unknown")  # type: ignore

                                # Submission date
                                with div(cls="pending-post-date"):  # type: ignore
                                    if hasattr(pending_post, "created_at"):
                                        text(f"Submitted on: {pending_post.created_at}")  # type: ignore

                        # Moderation controls
                        # Check if user is the author of the post
                        is_owner = (
                            user
                            and hasattr(pending_post, "author")
                            and pending_post.author
                            and pending_post.author.id == user.id
                        )
                        if is_admin or is_owner:
                            with div(cls="moderation-controls"):  # type: ignore
                                with form(
                                    action=f"/html/pending-posts/{pending_post.id}/moderate/",
                                    method="post",
                                ):  # type: ignore
                                    input_(
                                        type="hidden", name="action", value="approve"
                                    )  # type: ignore
                                    button(
                                        "APPROVE POST",
                                        type="submit",
                                        cls="approve-button",
                                    )  # type: ignore

                                with form(
                                    action=f"/html/pending-posts/{pending_post.id}/moderate/",
                                    method="post",
                                ):  # type: ignore
                                    input_(type="hidden", name="action", value="reject")  # type: ignore
                                    input_(
                                        type="text",
                                        name="moderation_reason",
                                        placeholder="Reason for rejection",
                                    )  # type: ignore
                                    button(
                                        "REJECT POST",
                                        type="submit",
                                        cls="reject-button",
                                    )  # type: ignore

            # Pagination controls
            if pagination:
                with div(cls="pagination"):  # type: ignore
                    # Build the base URL for pagination links
                    base_url = "/html/pending-posts/"

                    if pagination["has_previous"]:
                        a(
                            "Previous",
                            href=f"{base_url}?page={pagination['previous_page']}",
                        )  # type: ignore

                    span(
                        f"Page {pagination['current_page']} of {pagination['total_pages']}"  # noqa: E501
                    )  # type: ignore

                    if pagination.get("has_next"):
                        a("Next", href=f"{base_url}?page={pagination['next_page']}")  # type: ignore
        else:
            p("NO PENDING POSTS FOUND")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="The Robot Overlord - Pending Posts",
        user=user,
        messages=messages,
        content_func=content_func,
    )
