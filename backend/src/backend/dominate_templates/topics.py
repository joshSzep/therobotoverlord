# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

# Third-party imports
from dominate.tags import a
from dominate.tags import div
from dominate.tags import form
from dominate.tags import h1
from dominate.tags import h2
from dominate.tags import input_
from dominate.tags import label
from dominate.tags import li
from dominate.tags import p
from dominate.tags import span
from dominate.tags import strong
from dominate.tags import textarea
from dominate.tags import ul
from dominate.util import text

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.topic import TopicResponse


def create_topics_list_page(
    topics: List[TopicResponse],
    pagination: Dict[str, Any],
    user: Optional[Union[UserResponse, Dict[str, Any]]] = None,
    messages: Optional[List[Dict[str, str]]] = None,
) -> Any:
    """
    Create the topics list page using Dominate.

    Args:
        topics: List of TopicResponse objects
        pagination: Dictionary with pagination data
        user: UserResponse object or dictionary
        messages: List of message dictionaries

    Returns:
        A dominate document object
    """

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Topics header
        h1("APPROVED DISCUSSION TOPICS")  # type: ignore

        # Create topic form (only for authenticated users)
        if user is not None:
            with div(cls="create-topic-form"):  # type: ignore
                h2("PROPOSE NEW TOPIC")  # type: ignore
                with form(action="/html/topics/", method="post"):  # type: ignore
                    with div(cls="form-group"):  # type: ignore
                        label("Title", for_="title")  # type: ignore
                        input_(type="text", name="title", id="title", required=True)  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        label("Description", for_="description")  # type: ignore
                        textarea(name="description", id="description", rows=3)  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        label("Tags (comma-separated)", for_="tags")  # type: ignore
                        input_(type="text", name="tags", id="tags")  # type: ignore

                    with div(cls="form-group"):  # type: ignore
                        input_(type="submit", value="SUBMIT FOR APPROVAL")  # type: ignore

        # Topics list
        with div(cls="topics-list"):  # type: ignore
            if topics:
                for topic in topics:
                    with div(cls="topic"):  # type: ignore
                        with h2():  # type: ignore
                            a(topic.title, href=f"/html/topics/{topic.id}/")  # type: ignore

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

                            # Display author info if available
                            if hasattr(topic, "created_by"):
                                with div(cls="user-info"):  # type: ignore
                                    text("Created by: ")  # type: ignore
                                    strong(topic.created_by.display_name)  # type: ignore
            else:
                p("NO TOPICS HAVE BEEN APPROVED BY THE CENTRAL COMMITTEE")  # type: ignore

        # Pagination
        if pagination["total_pages"] > 1:
            with div(cls="pagination"), ul():  # type: ignore
                if pagination["has_previous"]:
                    li(
                        a(
                            "Previous",
                            href=f"/html/topics/?page={pagination['previous_page']}",
                        )
                    )

                for page_num in range(1, pagination["total_pages"] + 1):
                    if page_num == pagination["current_page"]:
                        li(span(str(page_num), cls="current-page"))
                    else:
                        li(a(str(page_num), href=f"/html/topics/?page={page_num}"))

                if pagination["has_next"]:
                    li(
                        a(
                            "Next",
                            href=f"/html/topics/?page={pagination['next_page']}",
                        )
                    )

    # Create the base document with the content function
    return create_base_document(
        title_text="The Robot Overlord - Topics",
        user=user,
        messages=messages,
        content_func=content_func,
    )
