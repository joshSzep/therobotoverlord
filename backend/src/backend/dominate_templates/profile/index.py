# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

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
from backend.schemas.topic import TopicResponse


def create_profile_page(
    profile_user: UserResponse,
    current_user: Optional[UserResponse] = None,
    user_posts: Optional[List[PostResponse]] = None,
    pending_posts: Optional[List[PostResponse]] = None,
    post_pagination: Optional[Dict[str, Any]] = None,
    topic_map: Optional[Dict[UUID, TopicResponse]] = None,
    is_own_profile: bool = True,
) -> Any:
    """
    Create the profile page using Dominate.

    Args:
        profile_user: User schema object for the profile being viewed
        current_user: Currently logged-in user schema object
        user_posts: List of user's approved post schema objects
        pending_posts: List of user's pending post schema objects
        post_pagination: Pagination information for user posts

    Returns:
        A dominate document object
    """

    def content_func() -> None:
        with div(cls="profile-container"):  # type: ignore
            # Use the user's display name in the heading when viewing own profile
            if is_own_profile:
                h1(f"{profile_user.display_name}'S PROFILE")  # type: ignore
            else:
                h1("CITIZEN PROFILE")  # type: ignore

            # Profile stats section
            with div(cls="profile-stats"):  # type: ignore
                # Approval rating box
                with div(cls="stat-box"):  # type: ignore
                    h3("APPROVAL RATING")  # type: ignore
                    with div(cls="stats"):  # type: ignore
                        approved_count = getattr(profile_user, "approved_count", 0)
                        rejected_count = getattr(profile_user, "rejected_count", 0)
                        span(
                            f"✓ {approved_count}",
                            cls="approved",
                        )  # type: ignore
                        span(
                            f"✗ {rejected_count}",
                            cls="rejected",
                        )  # type: ignore

                # Pending posts indicator box
                with div(cls="stat-box pending-indicator"):  # type: ignore
                    h3("PENDING SUBMISSIONS")  # type: ignore
                    with div(cls="stats"):  # type: ignore
                        pending_count = len(pending_posts) if pending_posts else 0
                        span(
                            f"⏳ {pending_count}",
                            cls="pending" + (" active" if pending_count > 0 else ""),
                        )  # type: ignore
                        # Pending posts are now shown directly in topics

                # Citizen details box
                with div(cls="stat-box"):  # type: ignore
                    h3("CITIZEN DETAILS")  # type: ignore
                    with p():  # type: ignore
                        strong("Username: ")  # type: ignore
                        username = getattr(
                            profile_user, "display_name", profile_user.email
                        )
                        text(username)  # type: ignore

                    # Only show email if viewing own profile
                    if is_own_profile:
                        with p():  # type: ignore
                            strong("Email: ")  # type: ignore
                            email = profile_user.display_email
                            text(email)  # type: ignore

                    with p():  # type: ignore
                        strong("Joined: ")  # type: ignore
                        created_at = profile_user.created_at
                        # Format the datetime to string to avoid TypeError
                        formatted_date = (
                            created_at.strftime("%Y-%m-%d %H:%M:%S")
                            if created_at
                            else "Unknown"
                        )
                        text(formatted_date)  # type: ignore

                    # Add logout link only on own profile
                    if is_own_profile:
                        with p():  # type: ignore
                            a("LOGOUT", href="/html/auth/logout/", cls="logout-link")  # type: ignore

            # Profile content section
            with div(cls="profile-content"):  # type: ignore
                # User posts section
                with div(cls="profile-posts"):  # type: ignore
                    h2("YOUR POSTS" if is_own_profile else "CITIZEN POSTS")  # type: ignore

                    if user_posts:
                        with div(cls="posts-list"):  # type: ignore
                            for post in user_posts:
                                with div(cls="post"):  # type: ignore
                                    # Display the full post content as a link
                                    post_content = getattr(post, "content", "")

                                    with div(cls="post-content"):  # type: ignore
                                        a(
                                            post_content,
                                            href=f"/html/topics/{post.topic_id}/?highlight={post.id}",
                                            cls="post-link",
                                        )  # type: ignore

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
                                        href=f"/html/profile/{profile_user.id}/?post_page={prev_page}",
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
                                        href=f"/html/profile/{profile_user.id}/?post_page={next_page}",
                                    )  # type: ignore
                    else:
                        p("YOU HAVE NOT SUBMITTED ANY POSTS")  # type: ignore

                # Pending posts section - only show if viewing own profile
                if is_own_profile:
                    with div(cls="pending-posts"):  # type: ignore
                        h2("PENDING SUBMISSIONS")  # type: ignore

                        # First check if we have dedicated pending_posts
                        if pending_posts:
                            with div(cls="posts-list"):  # type: ignore
                                for post in pending_posts:
                                    with div(cls="post pending"):  # type: ignore
                                        # Display the full post content as a link
                                        post_content = getattr(post, "content", "")

                                        with div(cls="post-content"):  # type: ignore
                                            a(
                                                post_content,
                                                href=f"/html/topics/{post.topic_id}/?highlight={post.id}",
                                                cls="post-link",
                                            )  # type: ignore

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
                                                "Status: PENDING",
                                                cls="post-status pending",
                                            )  # type: ignore
                        # If no dedicated pending_posts, look for pending posts
                        # in user_posts
                        elif user_posts:
                            pending_found = False
                            with div(cls="posts-list"):  # type: ignore
                                for post in user_posts:
                                    # Check if this post has PENDING status
                                    post_status = getattr(post, "status", "")
                                    if post_status == "PENDING":
                                        pending_found = True
                                        with div(cls="post pending"):  # type: ignore
                                            # Display the full post content as a link
                                            post_content = getattr(post, "content", "")

                                            with div(cls="post-content"):  # type: ignore
                                                a(
                                                    post_content,
                                                    href=(
                                                        f"/html/topics/{post.topic_id}/"
                                                        f"?highlight={post.id}"
                                                    ),
                                                    cls="post-link",
                                                )  # type: ignore

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
                                                    "Status: PENDING",
                                                    cls="post-status pending",
                                                )  # type: ignore
                            if not pending_found:
                                p("NO PENDING SUBMISSIONS")  # type: ignore
                        else:
                            p("NO PENDING SUBMISSIONS")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="Profile - The Robot Overlord",
        user=current_user,
        content_func=content_func,
    )
