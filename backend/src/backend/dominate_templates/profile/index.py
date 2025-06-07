# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third-party imports
from dominate.tags import a
from dominate.tags import div
from dominate.tags import h1
from dominate.tags import h2
from dominate.tags import h3
from dominate.tags import p
from dominate.tags import span
from dominate.tags import strong
from dominate.util import text

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.post import PostResponse


def create_profile_page(
    user: UserResponse,
    user_posts: Optional[List[PostResponse]] = None,
    pending_posts: Optional[List[PostResponse]] = None,
    post_pagination: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Create the profile page using Dominate.

    Args:
        user: User schema object
        user_posts: List of user's approved post schema objects
        pending_posts: List of user's pending post schema objects
        post_pagination: Pagination information for user posts

    Returns:
        A dominate document object
    """
    # Define the content function to be passed to the base document

    # Define the content function to be passed to the base document
    def content_func() -> None:
        with div(cls="profile-container"):  # type: ignore
            h1("CITIZEN PROFILE")  # type: ignore

            # Profile stats section
            with div(cls="profile-stats"):  # type: ignore
                # Approval rating box
                with div(cls="stat-box"):  # type: ignore
                    h3("APPROVAL RATING")  # type: ignore
                    with div(cls="stats"):  # type: ignore
                        approved_count = getattr(user, "approved_count", 0)
                        rejected_count = getattr(user, "rejected_count", 0)
                        span(
                            f"✓ {approved_count}",
                            cls="approved",
                        )  # type: ignore
                        span(
                            f"✗ {rejected_count}",
                            cls="rejected",
                        )  # type: ignore

                # Citizen details box
                with div(cls="stat-box"):  # type: ignore
                    h3("CITIZEN DETAILS")  # type: ignore
                    with p():  # type: ignore
                        strong("Username: ")  # type: ignore
                        username = getattr(user, "display_name", user.email)
                        text(username)  # type: ignore

                    with p():  # type: ignore
                        strong("Email: ")  # type: ignore
                        email = user.email
                        text(email)  # type: ignore

                    with p():  # type: ignore
                        strong("Joined: ")  # type: ignore
                        created_at = user.created_at
                        text(created_at)  # type: ignore

            # Profile content section
            with div(cls="profile-content"):  # type: ignore
                # User posts section
                with div(cls="profile-posts"):  # type: ignore
                    h2("YOUR POSTS")  # type: ignore

                    if user_posts:
                        with div(cls="posts-list"):  # type: ignore
                            for post in user_posts:
                                with div(cls="post"):  # type: ignore
                                    with h3():  # type: ignore
                                        # Get post attributes from schema
                                        post_title = getattr(
                                            post, "title", "Untitled Post"
                                        )
                                        post_id = post.id
                                        a(
                                            post_title,
                                            href=f"/html/posts/{post_id}/",
                                        )  # type: ignore

                                    # Truncate content to 100 characters
                                    post_content = getattr(post, "content", "")
                                    content = post_content
                                    if len(content) > 100:
                                        content = content[:97] + "..."
                                    p(content)  # type: ignore

                                    with div(cls="post-meta"):  # type: ignore
                                        with span():  # type: ignore
                                            text("Topic: ")  # type: ignore
                                            topic_id = post.topic_id
                                            topic_title = "View Topic"

                                            a(
                                                topic_title,
                                                href=f"/html/topics/{topic_id}/",
                                            )  # type: ignore

                                        post_created_at = post.created_at
                                        post_status = getattr(post, "status", "PENDING")

                                        span(f"Posted: {post_created_at}")  # type: ignore
                                        span(
                                            f"Status: {post_status}",
                                            cls=f"post-status {post_status.lower()}",
                                        )  # type: ignore

                        # Pagination controls
                        if post_pagination:
                            with div(cls="pagination"):  # type: ignore
                                # Use safer attribute access for pagination dictionary
                                has_previous = post_pagination.get(
                                    "has_previous", False
                                )
                                if has_previous:
                                    prev_page = post_pagination.get("previous_page", 1)
                                    a(
                                        "Previous",
                                        href=f"/html/profile/?post_page={prev_page}",
                                    )  # type: ignore

                                current_page = post_pagination.get("current_page", 1)
                                total_pages = post_pagination.get("total_pages", 1)
                                span(
                                    f"Page {current_page} of {total_pages}"  # noqa: E501
                                )  # type: ignore

                                has_next = post_pagination.get("has_next", False)
                                if has_next:
                                    next_page = post_pagination.get("next_page", 1)
                                    a(
                                        "Next",
                                        href=f"/html/profile/?post_page={next_page}",
                                    )  # type: ignore
                    else:
                        p("YOU HAVE NOT SUBMITTED ANY POSTS")  # type: ignore

                # Pending posts section
                with div(cls="pending-posts"):  # type: ignore
                    h2("PENDING SUBMISSIONS")  # type: ignore

                    if pending_posts:
                        with div(cls="posts-list"):  # type: ignore
                            for post in pending_posts:
                                with div(cls="post pending"):  # type: ignore
                                    # Get post title
                                    post_title = getattr(post, "title", "Untitled Post")
                                    h3(post_title)  # type: ignore

                                    # Truncate content to 100 characters
                                    post_content = getattr(post, "content", "")
                                    content = post_content
                                    if len(content) > 100:
                                        content = content[:97] + "..."
                                    p(content)  # type: ignore

                                    with div(cls="post-meta"):  # type: ignore
                                        with span():  # type: ignore
                                            text("Topic: ")  # type: ignore
                                            topic_id = post.topic_id
                                            topic_title = "View Topic"

                                            a(
                                                topic_title,
                                                href=f"/html/topics/{topic_id}/",
                                            )  # type: ignore

                                        # Get created_at from schema
                                        post_created_at = post.created_at
                                        span(f"Submitted: {post_created_at}")  # type: ignore
                                        span(
                                            "Status: PENDING", cls="post-status pending"
                                        )  # type: ignore
                    else:
                        p("NO PENDING SUBMISSIONS")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="Profile - The Robot Overlord", user=user, content_func=content_func
    )
