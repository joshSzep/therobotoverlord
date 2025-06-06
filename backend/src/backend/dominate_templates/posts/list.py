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
from dominate.tags import p
from dominate.tags import span
from dominate.tags import time_

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


def create_posts_list_page(
    posts: List[PostResponse],
    pagination: Dict[str, Any],
    user: Optional[UserResponse] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    topic_map: Optional[Dict[UUID, TopicResponse]] = None,
) -> Any:
    """
    Create the posts list page using Dominate.

    Args:
        posts: List of PostResponse objects
        pagination: Pagination information
        user: UserResponse object
        messages: List of message dictionaries

    Returns:
        A dominate document object
    """

    # Define the content function to be passed to the base document
    def content_func() -> None:
        h1("APPROVED POSTS FOR DISCUSSION")  # type: ignore

        if posts:
            with div(cls="posts-list"):  # type: ignore
                for post in posts:
                    with div(cls="post"):  # type: ignore
                        # Use schema object content as a permalink to the post detail
                        if post.content:
                            # Make the content a permalink to the post detail
                            with p():  # type: ignore
                                a(post.content, href=f"/html/posts/{post.id}/")  # type: ignore

                        with div(cls="post-meta"):  # type: ignore
                            # Display author if available
                            if post.author:
                                with span(cls="author"):  # type: ignore
                                    span("By: ")  # type: ignore
                                    a(
                                        post.author.display_name,
                                        href=f"/html/profile/{post.author.id}/",
                                    )  # type: ignore

                            # Display topic name if available, otherwise ID
                            with span(cls="topic"):  # type: ignore
                                topic_url = f"/html/topics/{post.topic_id}/"
                                topic_name = "Unknown Topic"
                                if topic_map and post.topic_id in topic_map:
                                    topic_name = topic_map[post.topic_id].title
                                a(topic_name, href=topic_url)  # type: ignore

                            # Display created_at
                            with span(cls="date"):  # type: ignore
                                span(" on ")  # type: ignore
                                time_(
                                    post.created_at.strftime("%Y-%m-%d %H:%M"),
                                    datetime=post.created_at.isoformat(),
                                )  # type: ignore

            # Pagination controls
            if pagination:
                with div(cls="pagination"):  # type: ignore
                    if pagination["has_previous"]:
                        a(
                            "Previous",
                            href=f"/html/posts/?page={pagination['previous_page']}",
                        )  # type: ignore

                    span(
                        f"Page {pagination['current_page']} of {pagination['total_pages']}"  # noqa: E501
                    )  # type: ignore

                    if pagination.get("has_next"):
                        a("Next", href=f"/html/posts/?page={pagination['next_page']}")  # type: ignore
        else:
            p("NO POSTS HAVE BEEN APPROVED BY THE CENTRAL COMMITTEE")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="The Robot Overlord - Posts",
        user=user,
        messages=messages,
        content_func=content_func,
    )
