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
                    with div(cls="topic"):  # type: ignore
                        with h2():  # type: ignore
                            # Use schema object attributes directly
                            a(topic.title, href=f"/html/topics/{topic.id}/")  # type: ignore

                        # Use schema object description
                        if topic.description:
                            p(topic.description)  # type: ignore

                        with div(cls="topic-meta"):  # type: ignore
                            # Display post count if available
                            if hasattr(topic, "post_count"):
                                span(f"{topic.post_count} posts")  # type: ignore

                            # Display tags if available
                            if topic.tags:
                                with div(cls="topic-tags"):  # type: ignore
                                    for tag in topic.tags:
                                        span(tag.name, cls="tag")  # type: ignore

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

        # Create topic form section (only if user is logged in)
        if user:
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
