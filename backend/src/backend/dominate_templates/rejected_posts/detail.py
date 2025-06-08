from dominate.tags import a
from dominate.tags import div
from dominate.tags import h2
from dominate.tags import hr
from dominate.tags import p
from dominate.tags import pre
from dominate.tags import span

from backend.dominate_templates.base import create_base_page
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.rejected_post import RejectedPostResponse


def create_rejected_post_detail_page(
    rejected_post: RejectedPostResponse,
    is_admin: bool,
    current_user: UserResponse,
) -> str:
    """
    Create a page that displays a rejected post detail.

    Args:
        rejected_post: The rejected post to display
        is_admin: Whether the current user is an admin
        current_user: The current user

    Returns:
        str: HTML content for the rejected post detail page
    """
    doc = create_base_page(
        title="Rejected Post",
        current_user=current_user,
        is_admin=is_admin,
    )

    with doc, div(cls="container mt-4"):  # type: ignore
        # Back button
        with div(cls="mb-3"):  # type: ignore
            a(
                "← Back to Rejected Posts",
                href="/html/rejected-posts/",
                cls="btn btn-outline-secondary",
            )  # type: ignore

        # Main content
        with (
            div(cls="card mb-4"),  # type: ignore
            div(  # type: ignore
                cls="card-header bg-danger text-white d-flex "
                "justify-content-between align-items-center"
            ),
        ):
            h2("Rejected Post", cls="h5 mb-0")  # type: ignore[no-untyped-call]
            span(f"ID: {rejected_post.id}", cls="badge bg-light text-dark")  # type: ignore[no-untyped-call]

        with div(cls="card-body"):  # type: ignore
            # Topic information
            with div(cls="mb-3"):  # type: ignore
                span("Topic: ", cls="fw-bold")  # type: ignore[no-untyped-call]
                if hasattr(rejected_post, "topic") and rejected_post.topic:
                    # Get topic title safely using dictionary access
                    topic_title = rejected_post.topic.get("title", "Unknown")
                    a(
                        topic_title,
                        href=f"/html/topics/{rejected_post.topic_id}/",
                        cls="badge bg-secondary text-decoration-none",
                    )  # type: ignore[no-untyped-call]
                else:
                    span(f"Topic {rejected_post.topic_id}")  # type: ignore[no-untyped-call]

            # Author information
            with div(cls="mb-3"):  # type: ignore
                span("Author: ", cls="fw-bold")  # type: ignore[no-untyped-call]
                if rejected_post.author:
                    a(
                        rejected_post.author.display_name,
                        href=f"/html/users/{rejected_post.author.id}/",
                        cls="text-decoration-none",
                    )  # type: ignore[no-untyped-call]
                    if rejected_post.author.id == current_user.id:
                        span(" (You)", cls="text-muted")  # type: ignore[no-untyped-call]
                else:
                    span("[Author data unavailable]", cls="text-muted")  # type: ignore[no-untyped-call]

            # Post date
            with div(cls="mb-3"):  # type: ignore
                span("Created: ", cls="fw-bold")  # type: ignore
                span(rejected_post.created_at.strftime("%Y-%m-%d %H:%M:%S"))  # type: ignore[no-untyped-call]

            hr()  # type: ignore

            # Post content
            with div(cls="mb-4"):  # type: ignore
                h2("Content", cls="h5 mb-2")  # type: ignore
                with div(cls="p-3 bg-light rounded"):  # type: ignore
                    pre(rejected_post.content, cls="mb-0")  # type: ignore

            # Rejection reason
            with div(cls="alert alert-danger"):  # type: ignore
                h2("Rejection Reason", cls="h5 mb-2")  # type: ignore
                p(rejected_post.moderation_reason)  # type: ignore

            # Actions section
            with div(cls="card mb-4"):  # type: ignore
                with div(cls="card-header bg-secondary text-white"):  # type: ignore
                    h2("Actions", cls="h5 mb-0")  # type: ignore

                with div(cls="card-body"), div(cls="d-flex gap-2"):  # type: ignore
                    # Only show actions to admins
                    if is_admin:
                        a(
                            "Edit and Resubmit",
                            href=f"/html/resubmit-post/{rejected_post.id}/",
                            cls="btn btn-primary",
                        )  # type: ignore
                        a(
                            "Delete Permanently",
                            href=f"/html/rejected-posts/{rejected_post.id}/delete/",
                            cls="btn btn-danger",
                        )  # type: ignore
                    else:
                        p(
                            "CITIZEN, YOUR POST HAS BEEN REJECTED.",
                            cls="text-danger fw-bold mb-0",
                        )  # type: ignore

    return str(doc.render())
