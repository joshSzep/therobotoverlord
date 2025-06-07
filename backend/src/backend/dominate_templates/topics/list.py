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
from dominate.tags import label
from dominate.tags import p
from dominate.tags import span
from dominate.tags import textarea
from dominate.util import text

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.topic import TopicResponse


def create_topics_list_page(
    topics: List[TopicResponse],
    pagination: Dict[str, Any],
    user: Optional[UserResponse] = None,
    messages: Optional[List[Dict[str, str]]] = None,
) -> Any:
    """
    Create the topics list page using Dominate.

    Args:
        topics: List of TopicResponse objects
        pagination: Pagination information
        user: UserResponse object
        messages: List of message dictionaries

    Returns:
        A dominate document object
    """
    # Define the content function to be passed to the base document

    # Define the content function to be passed to the base document
    def content_func() -> None:
        h1("APPROVED TOPICS FOR DISCUSSION")  # type: ignore

        if topics:
            with div(cls="topics-list"):  # type: ignore
                for topic in topics:
                    with div(cls="topic-card"):  # type: ignore
                        # Topic header with title
                        with div(cls="topic-header"), h2():  # type: ignore
                            a(
                                topic.title,
                                href=f"/html/topics/{topic.id}/",
                                cls="topic-title-link",
                            )  # type: ignore

                        # Topic content section
                        with div(cls="topic-content"):  # type: ignore
                            # Description
                            if topic.description:
                                with div(cls="topic-description"):  # type: ignore
                                    p(topic.description)  # type: ignore

                            # Topic metadata section
                            with div(cls="topic-meta"):  # type: ignore
                                # Tags section
                                with div(cls="topic-tags"):  # type: ignore
                                    if topic.tags:
                                        for tag in topic.tags:
                                            span(tag.name, cls="tag")  # type: ignore
                                    else:
                                        span("No tags", cls="no-tags")  # type: ignore

                                # Stats section
                                with div(cls="topic-stats"):  # type: ignore
                                    # Post count
                                    with div(cls="post-count"):  # type: ignore
                                        post_count = getattr(topic, "post_count", 0)
                                        span(f"{post_count} posts", cls="count")  # type: ignore

                                    # Display author info if available
                                    if hasattr(topic, "author"):
                                        with div(cls="author-info"):  # type: ignore
                                            text("Created by: ")  # type: ignore
                                            author = topic.author
                                            author_name = getattr(
                                                author, "display_name", "Unknown"
                                            )
                                            author_id = getattr(author, "id", None)
                                            if author_id:
                                                href = f"/html/profile/{author_id}/"
                                                a(author_name, href=href)  # type: ignore
                                            else:
                                                text(author_name)  # type: ignore

            # Pagination controls
            if pagination:
                with div(cls="pagination"):  # type: ignore
                    if pagination["has_previous"]:
                        a(
                            "Previous",
                            href=f"/html/topics/?page={pagination['previous_page']}",
                        )  # type: ignore

                    span(
                        f"Page {pagination['current_page']} of {pagination['total_pages']}"  # noqa: E501
                    )  # type: ignore

                    if pagination.get("has_next"):
                        a("Next", href=f"/html/topics/?page={pagination['next_page']}")  # type: ignore
        else:
            p("NO TOPICS HAVE BEEN APPROVED BY THE CENTRAL COMMITTEE")  # type: ignore

        # Create topic form section (only if user is an admin)
        if user and user.is_admin:
            with div(cls="create-topic"):  # type: ignore
                h2("PROPOSE NEW TOPIC")  # type: ignore
                with form(action="/html/topics/", method="post"):  # type: ignore
                    with div(cls="form-group"):  # type: ignore
                        label("Title:", for_="title")  # type: ignore
                        input_(type="text", id="title", name="title", required=True)  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        label("Description:", for_="description")  # type: ignore
                        textarea(
                            id="description",
                            name="description",
                            rows="4",
                            required=True,
                        )  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        label("Tags (comma separated):", for_="tags")  # type: ignore
                        input_(type="text", id="tags", name="tags")  # type: ignore

                    button("SUBMIT FOR APPROVAL", type="submit")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="The Robot Overlord - Topics",
        user=user,
        messages=messages,
        content_func=content_func,
    )
