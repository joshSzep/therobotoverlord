# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third-party imports
from dominate.tags import a
from dominate.tags import br
from dominate.tags import div
from dominate.tags import form
from dominate.tags import h1
from dominate.tags import h2
from dominate.tags import input_
from dominate.tags import label
from dominate.tags import p
from dominate.tags import span
from dominate.tags import strong
from dominate.tags import textarea
from dominate.util import text

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.post import PostResponse


def create_post_detail_page(
    post: PostResponse,
    replies: Optional[List[PostResponse]] = None,
    pagination: Optional[Dict[str, Any]] = None,
    user: Optional[UserResponse] = None,
) -> Any:
    """
    Create the post detail page using Dominate.

    Args:
        post: PostResponse object
        replies: List of PostResponse objects
        pagination: Pagination information
        user: UserResponse object

    Returns:
        A dominate document object
    """
    # Get post title for document title
    post_title = getattr(post, "title", "Post Detail")

    # Define the content function to be passed to the base document

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Post detail section
        with div(cls="post-detail"):  # type: ignore
            with div(cls="post-header"):  # type: ignore
                post_title = "Post Detail"  # Default title
                h1(post_title)  # type: ignore

                with div(cls="post-meta"):  # type: ignore
                    with div(cls="user-info"):  # type: ignore
                        # Access author directly from post schema
                        author = post.author

                        # Display author name as a deep link to profile
                        with strong():  # type: ignore
                            a(author.display_name, href=f"/html/profile/{author.id}/")  # type: ignore

                        # Handle stats
                        with div(cls="stats"):  # type: ignore
                            # Display counts with shorter format
                            span(f"✓ {author.approved_count}", cls="approved")  # type: ignore
                            span(f"✗ {author.rejected_count}", cls="rejected")  # type: ignore

                    # Handle topic using topic_id from PostResponse
                    topic_id = post.topic_id
                    # Use a placeholder since PostResponse doesn't have topic title
                    topic_title = "View Topic"

                    with span():  # type: ignore
                        text("Topic: ")  # type: ignore
                        a(topic_title, href=f"/html/topics/{topic_id}/")  # type: ignore

                    # Handle created_at directly from schema
                    span(f"Posted: {post.created_at}")  # type: ignore

            # Post content with newlines preserved
            with div(cls="post-content"):  # type: ignore
                # Get content directly from schema and convert newlines to <br> tags
                content_lines = post.content.split("\n")
                for i, line in enumerate(content_lines):
                    text(line)  # type: ignore
                    if i < len(content_lines) - 1:
                        # Add a <br> tag after each line except the last one
                        with div(style="display: none;"):  # type: ignore
                            br()  # type: ignore

        # Replies section
        with div(cls="post-replies"):  # type: ignore
            h2("APPROVED REPLIES")  # type: ignore

            if replies:
                with div(cls="replies-list"):  # type: ignore
                    for reply in replies:
                        with div(cls="post reply"):  # type: ignore
                            with div(cls="user-info"):  # type: ignore
                                # Access author directly from reply schema
                                author = reply.author

                                # Display author name as a deep link to profile
                                with strong():  # type: ignore
                                    href = f"/html/profile/{author.id}/"
                                    a(author.display_name, href=href)  # type: ignore

                                # Handle stats
                                with div(cls="stats"):  # type: ignore
                                    # Display counts with shorter format
                                    span(f"✓ {author.approved_count}", cls="approved")  # type: ignore
                                    span(f"✗ {author.rejected_count}", cls="rejected")  # type: ignore

                            # Reply content with newlines preserved
                            with div(cls="reply-content"):  # type: ignore
                                content_lines = reply.content.split("\n")
                                for i, line in enumerate(content_lines):
                                    text(line)  # type: ignore
                                    if i < len(content_lines) - 1:
                                        # Add a <br> tag after each line except last one
                                        with div(style="display: none;"):  # type: ignore
                                            br()  # type: ignore

                            with div(cls="post-meta"):  # type: ignore
                                # Handle created_at directly from schema
                                span(f"Posted: {reply.created_at}")  # type: ignore

                # Pagination controls
                # Pagination controls using dictionary access for pagination info
                # and schema object for post.id
                if pagination:
                    with div(cls="pagination"):  # type: ignore
                        # Previous page link
                        if pagination.get("has_previous"):
                            post_id = post.id
                            prev_page = pagination["previous_page"]
                            prev_url = f"/html/posts/{post_id}/?page={prev_page}"
                            a("Previous", href=prev_url)  # type: ignore

                        # Current page indicator
                        current = pagination["current_page"]
                        total = pagination["total_pages"]
                        span(f"Page {current} of {total}")  # type: ignore

                        # Next page link
                        if pagination.get("has_next"):
                            post_id = post.id
                            next_page = pagination["next_page"]
                            next_url = f"/html/posts/{post_id}/?page={next_page}"
                            a("Next", href=next_url)  # type: ignore
            else:
                p("NO REPLIES HAVE BEEN APPROVED FOR THIS POST")  # type: ignore

        # Reply form section (only if user is logged in)
        if user:
            with div(cls="create-reply"):  # type: ignore
                h2("SUBMIT REPLY")  # type: ignore
                # Access post.id directly from schema
                post_id = post.id

                # Create form with action using post_id
                form_action = f"/html/posts/{post_id}/reply/"
                with form(action=form_action, method="post"):  # type: ignore
                    with div(cls="form-group"):  # type: ignore
                        label("Content:", for_="content")  # type: ignore
                        textarea(id="content", name="content", rows="4", required=True)  # type: ignore
                    with div(cls="form-group"):  # type: ignore
                        input_(type="submit", value="Submit Reply", cls="btn")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text=post_title, user=user, content_func=content_func
    )
