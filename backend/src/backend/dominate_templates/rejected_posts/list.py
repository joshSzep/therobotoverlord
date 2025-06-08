# Standard library imports
from typing import List

# Third-party imports
from dominate.tags import a
from dominate.tags import div
from dominate.tags import h1
from dominate.tags import p
from dominate.tags import span
from dominate.tags import table
from dominate.tags import tbody
from dominate.tags import td
from dominate.tags import th
from dominate.tags import thead
from dominate.tags import tr

# Project-specific imports
from backend.dominate_templates.base import create_base_page
from backend.dominate_templates.components.moderation_feedback import (
    create_moderation_feedback,
)
from backend.dominate_templates.components.pagination import create_pagination
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.rejected_post import RejectedPostResponse


def create_rejected_posts_list_page(
    rejected_posts: List[RejectedPostResponse],
    count: int,
    limit: int,
    offset: int,
    is_admin: bool,
    current_user: UserResponse,
) -> str:
    """
    Create a page that displays a list of rejected posts.

    Args:
        rejected_posts: List of rejected posts to display
        count: Total number of rejected posts
        limit: Number of rejected posts per page
        offset: Offset for pagination
        is_admin: Whether the current user is an admin
        current_user: The current user

    Returns:
        str: HTML content for the rejected posts list page
    """
    doc = create_base_page(
        title="Rejected Posts",
        current_user=current_user,
        is_admin=is_admin,
    )

    with doc, div(cls="container mt-4"):  # type: ignore
        h1("Rejected Posts", cls="mb-4 soviet-header")  # type: ignore

        if not rejected_posts:
            p("No rejected posts found.", cls="alert alert-info")  # type: ignore
        else:
            # Display rejected posts count
            with div(cls="mb-3"):  # type: ignore
                span(
                    f"Showing {min(offset + 1, count)}-"
                    f"{min(offset + limit, count)} of {count} rejected posts"
                )  # type: ignore

            # Create table for rejected posts
            with table(cls="table table-striped table-bordered"):  # type: ignore
                with thead(cls="thead-dark"), tr():  # type: ignore
                    th("Title")  # type: ignore
                    th("Content")  # type: ignore
                    th("Topic")  # type: ignore
                    th("Author")  # type: ignore
                    th("Rejection Reason")  # type: ignore
                    th("Date")  # type: ignore
                    th("Actions")  # type: ignore

                with tbody():  # type: ignore
                    for post in rejected_posts:
                        with tr():  # type: ignore
                            # Title column (using content preview as title)
                            with td():  # type: ignore
                                content_preview = (
                                    post.content[:50] + "..."
                                    if len(post.content) > 50
                                    else post.content
                                )
                                a(
                                    content_preview,
                                    href=f"/html/rejected-posts/{post.id}/",
                                    cls="text-decoration-none",
                                )  # type: ignore

                            # Content preview
                            with td():  # type: ignore
                                span(
                                    post.content[:100] + "..."
                                    if len(post.content) > 100
                                    else post.content
                                )  # type: ignore

                            # Topic
                            with td():  # type: ignore
                                if hasattr(post, "topic") and post.topic:
                                    # Get topic title safely using dictionary access
                                    topic_title = post.topic.get("title", "Unknown")
                                    a(
                                        topic_title,
                                        href=f"/html/topics/{post.topic_id}/",
                                        cls=("badge bg-secondary text-decoration-none"),
                                    )  # type: ignore[no-untyped-call]
                                else:
                                    span(f"Topic {post.topic_id}")  # type: ignore

                            # Author
                            with td():  # type: ignore
                                if post.author:
                                    with div():  # type: ignore
                                        a(
                                            f"{post.author.display_name}",
                                            href=f"/html/profile/{post.author.id}/",
                                            cls="text-decoration-none",
                                        )  # type: ignore
                                else:
                                    span("Unknown")  # type: ignore

                            # Rejection reason
                            with td():  # type: ignore
                                # Use our new moderation feedback component
                                create_moderation_feedback(
                                    feedback=post.moderation_reason,
                                    status="rejected",
                                    show_icon=True,
                                )

                            # Date
                            with td():  # type: ignore
                                span(post.created_at.strftime("%Y-%m-%d %H:%M"))  # type: ignore

                            # Actions
                            with td(), div(cls="d-flex gap-2"):  # type: ignore
                                a(
                                    "View",
                                    href=f"/html/rejected-posts/{post.id}/",
                                    cls="btn btn-sm btn-primary",
                                )  # type: ignore

            # Pagination
            if count > limit:
                with div(cls="mt-4"):  # type: ignore
                    create_pagination(
                        count=count,
                        limit=limit,
                        offset=offset,
                        base_url="/html/rejected-posts/",
                    )

    return str(doc.render())
