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
from dominate.tags import h3
from dominate.tags import input_
from dominate.tags import label
from dominate.tags import p
from dominate.tags import span
from dominate.tags import strong
from dominate.tags import textarea

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


def create_topic_detail_page(
    topic: TopicResponse,
    posts: Optional[List[PostResponse]] = None,
    pagination: Optional[Dict[str, Any]] = None,
    user: Optional[UserResponse] = None,
) -> Any:
    """
    Create the topic detail page using Dominate.

    Args:
        topic: Topic schema object
        posts: List of post schema objects
        pagination: Pagination information
        user: Optional user schema object

    Returns:
        A dominate document object
    """
    # Create the base document with the topic title
    doc = create_base_document(
        title_text=f"{topic.title} - The Robot Overlord",
        user=user,
    )

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Topic detail section
        with div(cls="topic-detail"):  # type: ignore
            h1(topic.title)  # type: ignore

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
                with div(cls="posts-list"):  # type: ignore
                    for post in posts:
                        with div(cls="post"):  # type: ignore
                            with div(cls="user-info"):  # type: ignore
                                # Get author info
                                author = post.author
                                username = author.display_name
                                approved_count = getattr(author, "approved_count", 0)
                                rejected_count = getattr(author, "rejected_count", 0)

                                strong(username)  # type: ignore
                                with div(cls="stats"):  # type: ignore
                                    span(
                                        f"✓ {approved_count}",
                                        cls="approved",
                                    )  # type: ignore
                                    span(
                                        f"✗ {rejected_count}",
                                        cls="rejected",
                                    )  # type: ignore

                            with h3():  # type: ignore
                                a(post.title, href=f"/html/posts/{post.id}/")  # type: ignore

                            # Truncate content to 150 characters
                            content = post.content
                            if len(content) > 150:
                                content = content[:147] + "..."
                            p(content)  # type: ignore

                            with div(cls="post-meta"):  # type: ignore
                                span(f"Posted: {post.created_at}")  # type: ignore

                # Pagination controls
                if pagination:
                    with div(cls="pagination"):  # type: ignore
                        if pagination.get("has_previous"):
                            a(
                                "Previous",
                                href=f"/html/topics/{topic.id}/?page={pagination['previous_page']}",
                            )  # type: ignore

                        span(
                            f"Page {pagination['current_page']} of {pagination['total_pages']}"  # noqa: E501
                        )  # type: ignore

                        if pagination.get("has_next"):
                            a(
                                "Next",
                                href=f"/html/topics/{topic.id}/?page={pagination['next_page']}",
                            )  # type: ignore
            else:
                p("NO POSTS HAVE BEEN APPROVED FOR THIS TOPIC")  # type: ignore

        # Create post form section (only if user is logged in)
        if user:
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

    # Set the content function in the base document
    doc.get_or_create_body().add(content_func)

    return doc
