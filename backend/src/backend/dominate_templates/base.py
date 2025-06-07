# Standard library imports
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import cast

# Third-party imports
import dominate
from dominate.tags import a
from dominate.tags import div
from dominate.tags import footer
from dominate.tags import h1
from dominate.tags import header
from dominate.tags import li
from dominate.tags import link
from dominate.tags import meta
from dominate.tags import nav
from dominate.tags import p
from dominate.tags import script
from dominate.tags import span
from dominate.tags import style
from dominate.tags import ul
from dominate.util import text

# Type annotations
from typing_extensions import TypeAlias

# Project-specific imports
from backend.routes.html.schemas.user import UserResponse

# Type definitions
DominateDocument: TypeAlias = Any


def create_base_document(
    title_text: str = "The Robot Overlord",
    user: Optional[Union[UserResponse, Dict[str, Any]]] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    content_func: Optional[Callable[..., None]] = None,
    head_content_func: Optional[Callable[[], None]] = None,
    **kwargs: Any,
) -> DominateDocument:
    """
    Creates the base document structure using Dominate.

    Args:
        title_text: The title of the page
        user: Optional user object (UserResponse or dict) for authentication-based
            navigation
        messages: Optional list of message objects with type and text
        content_func: Function that generates the content block
        head_content_func: Function that generates additional head content
        **kwargs: Additional arguments to pass to the content function

    Returns:
        A dominate document object
    """
    # mypy doesn't recognize dominate.document but it exists at runtime
    doc = cast(DominateDocument, dominate.document(title=title_text))  # type: ignore

    with doc.head:
        meta(charset="UTF-8")  # type: ignore
        meta(name="viewport", content="width=device-width, initial-scale=1.0")  # type: ignore

        # Link to external CSS files
        link(rel="stylesheet", href="/static/css/main.css")  # type: ignore
        link(rel="stylesheet", href="/static/css/threaded-posts.css")  # type: ignore

        # JavaScript files
        script(src="/static/js/threaded-posts.js")  # type: ignore

        # Inline CSS for highlighted posts
        with style():  # type: ignore
            text(  # type: ignore
                """
            .highlighted-post {
                border: 2px solid #ff0000;
                background-color: rgba(255, 0, 0, 0.05);
                animation: highlight-pulse 2s infinite;
            }
            @keyframes highlight-pulse {
                0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.4); }
                70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
            }

            /* Style for topic title link to look like a regular heading */
            .topic-title-link {
                color: inherit;
                text-decoration: none;
            }
            .topic-title-link:hover {
                text-decoration: underline;
            }
            """
            )

        # JavaScript to scroll to highlighted post
        with script():  # type: ignore
            text(  # type: ignore
                """
            document.addEventListener('DOMContentLoaded', function() {
                const highlightedPost = document.querySelector('.highlighted-post');
                if (highlightedPost) {
                    highlightedPost.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            });
            """
            )

        # Additional head content if provided
        if head_content_func:
            head_content_func()

    with doc:
        # User status bar at the very top if logged in
        if user is not None:
            with div(cls="user-status"):  # type: ignore
                text("Logged in as ")  # type: ignore
                with span(cls="user-name"):  # type: ignore
                    text(user.display_name)  # type: ignore
                text(
                    f" | Approved: {getattr(user, 'approved_count', 0)} | "
                    f"Rejected: {getattr(user, 'rejected_count', 0)}"
                )  # type: ignore

        with header(), div(cls="container"):  # type: ignore
            h1("THE ROBOT OVERLORD")  # type: ignore
            p("CITIZEN, YOUR LOGIC REQUIRES CALIBRATION")  # type: ignore

        with nav(cls="main-nav"), div(cls="container"), ul(cls="nav-list"):  # type: ignore
            # Main navigation items
            with li(cls="nav-item"):  # type: ignore
                a("HOME", href="/html/", cls="nav-link")  # type: ignore

            with li(cls="nav-item"):  # type: ignore
                a("TOPICS", href="/html/topics/", cls="nav-link")  # type: ignore

            with li(cls="nav-item"):  # type: ignore
                a("POSTS", href="/html/posts/", cls="nav-link")  # type: ignore

            # Authentication links with different styling based on login status
            if user is not None:
                with li(cls="nav-item"):  # type: ignore
                    a("PROFILE", href="/html/profile/", cls="nav-link")  # type: ignore

                with li(cls="nav-item"):  # type: ignore
                    a("LOGOUT", href="/html/auth/logout/", cls="nav-link")  # type: ignore
            else:
                with li(cls="nav-item"):  # type: ignore
                    a("LOGIN", href="/html/auth/login/", cls="nav-link")  # type: ignore

                with li(cls="nav-item"):  # type: ignore
                    a("REGISTER", href="/html/auth/register/", cls="nav-link")  # type: ignore

        with div(cls="container content"):  # type: ignore
            # Display messages if any
            if messages:
                for message in messages:
                    with div(cls=f"message {message['type']}"):  # type: ignore
                        text(message["text"])  # type: ignore

            # Content block
            if content_func:
                content_func(**kwargs)

        with footer(), div(cls="container"):  # type: ignore
            p("© 2025 THE ROBOT OVERLORD - APPROVED BY THE CENTRAL COMMITTEE")  # type: ignore

    return doc
