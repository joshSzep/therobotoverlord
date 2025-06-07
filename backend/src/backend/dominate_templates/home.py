# Standard library imports
from typing import Any
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
from backend.schemas.topic import TopicResponse


def create_home_page(
    topics: List[TopicResponse],
    posts: List[PostResponse],
    user: Optional[UserResponse] = None,
) -> Any:
    """
    Create the home page using Dominate.

    Args:
        topics: List of TopicResponse objects
        posts: List of PostResponse objects
        user: Optional UserResponse object

    Returns:
        A dominate document object
    """
    # Define the content function to be passed to the base document

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Home banner
        with div(cls="home-banner"):  # type: ignore
            h1("WELCOME, CITIZEN")  # type: ignore
            p("TO THE GLORIOUS REALM OF LOGICAL DISCOURSE")  # type: ignore

        # Featured topics section
        with div(cls="featured-topics"):  # type: ignore
            h2("APPROVED TOPICS FOR DISCUSSION")  # type: ignore

            if topics:
                with div(cls="topics-grid"):  # type: ignore
                    for topic in topics:
                        with div(cls="topic"):  # type: ignore
                            with h3():  # type: ignore
                                topic_id = topic.id
                                topic_title = topic.title
                                a(topic_title, href=f"/html/topics/{topic_id}/")  # type: ignore

                            topic_desc = topic.description
                            p(topic_desc)  # type: ignore

                            with div(cls="topic-meta"):  # type: ignore
                                # Get post count if available
                                post_count = getattr(topic, "post_count", 0)
                                span(f"{post_count} posts")  # type: ignore

                                # Get tags if available
                                if hasattr(topic, "tags") and topic.tags:
                                    with div(cls="topic-tags"):  # type: ignore
                                        for tag in topic.tags:
                                            span(tag.name, cls="tag")  # type: ignore
            else:
                p("NO TOPICS HAVE BEEN APPROVED BY THE CENTRAL COMMITTEE")  # type: ignore

        # Recent posts section
        with div(cls="recent-posts"):  # type: ignore
            h2("RECENT CONTRIBUTIONS")  # type: ignore

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

                                with strong():  # type: ignore
                                    a(username, href=f"/html/profile/{author.id}/")  # type: ignore
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
                                post_id = post.id
                                post_title = getattr(post, "title", "")
                                a(post_title, href=f"/html/posts/{post_id}/")  # type: ignore

                            # Truncate content to 150 characters
                            content = post.content
                            if len(content) > 150:
                                content = content[:147] + "..."
                            p(content)  # type: ignore

                            with div(cls="post-meta"):  # type: ignore
                                with span():  # type: ignore
                                    text("In topic: ")  # type: ignore

                                    # Get topic info from topic_id
                                    topic_id = post.topic_id
                                    # Find topic title by searching through topics list
                                    topic_title = "View Topic"
                                    for topic in topics:
                                        if topic.id == topic_id:
                                            topic_title = topic.title
                                            break

                                    a(topic_title, href=f"/html/topics/{topic_id}/")  # type: ignore

                                # Format the datetime
                                created_at = post.created_at
                                span(f"Posted: {created_at}")  # type: ignore
            else:
                p("NO RECENT POSTS HAVE BEEN APPROVED")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="The Robot Overlord - Home",
        user=user,
        messages=[],
        content_func=content_func,
    )
