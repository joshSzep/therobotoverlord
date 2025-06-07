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
from dominate.tags import meta
from dominate.tags import nav
from dominate.tags import p
from dominate.tags import style
from dominate.tags import ul
from dominate.util import raw
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

        # CSS styles
        with style():  # type: ignore
            # Using raw to insert CSS content
            raw(  # type: ignore[no-untyped-call]
                """
            /* Soviet propaganda aesthetic */
            :root {
                --red: #cc0000;
                --dark-red: #990000;
                --gold: #ffd700;
                --black: #000000;
                --white: #ffffff;
                --gray: #444444;
            }

            body {
                font-family: 'Courier New', monospace;
                background-color: var(--black);
                color: var(--white);
                margin: 0;
                padding: 0;
                line-height: 1.6;
            }

            .container {
                width: 90%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            header {
                background-color: var(--red);
                color: var(--gold);
                padding: 20px 0;
                text-align: center;
                border-bottom: 5px solid var(--gold);
            }

            header h1 {
                margin: 0;
                font-size: 2.5em;
                text-transform: uppercase;
                letter-spacing: 2px;
            }

            nav {
                background-color: var(--dark-red);
                padding: 10px 0;
            }

            nav ul {
                list-style: none;
                padding: 0;
                margin: 0;
                display: flex;
                justify-content: center;
            }

            nav ul li {
                margin: 0 15px;
            }

            nav ul li a {
                color: var(--gold);
                text-decoration: none;
                text-transform: uppercase;
                font-weight: bold;
                letter-spacing: 1px;
            }

            nav ul li a:hover {
                text-decoration: underline;
            }

            .content {
                padding: 20px 0;
            }

            footer {
                background-color: var(--dark-red);
                color: var(--gold);
                text-align: center;
                padding: 20px 0;
                margin-top: 40px;
                border-top: 5px solid var(--gold);
            }

            /* Form styles */
            form {
                background-color: var(--gray);
                padding: 20px;
                border: 2px solid var(--red);
                margin-bottom: 20px;
            }

            input, textarea, select {
                width: 100%;
                padding: 10px;
                margin-bottom: 15px;
                border: 1px solid var(--dark-red);
                background-color: var(--black);
                color: var(--white);
            }

            button {
                background-color: var(--red);
                color: var(--gold);
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                text-transform: uppercase;
                font-weight: bold;
                letter-spacing: 1px;
            }

            button:hover {
                background-color: var(--dark-red);
            }

            /* Topic and post styles */
            .topic, .post {
                background-color: var(--gray);
                padding: 15px;
                margin-bottom: 15px;
                border-left: 5px solid var(--red);
            }

            .topic h2, .post h2 {
                margin-top: 0;
                color: var(--gold);
            }

            .user-info {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }

            .user-info .stats {
                margin-left: 15px;
                font-size: 0.9em;
            }

            .approved {
                color: var(--gold);
            }

            .rejected {
                color: var(--red);
            }

            .message {
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 5px;
            }

            .message.error {
                background-color: var(--red);
                color: var(--white);
            }

            .message.success {
                background-color: var(--dark-red);
                color: var(--gold);
            }
            """
            )

        # Additional head content if provided
        if head_content_func:
            head_content_func()

    with doc:
        with header(), div(cls="container"):  # type: ignore
            h1("THE ROBOT OVERLORD")  # type: ignore
            p("CITIZEN, YOUR LOGIC REQUIRES CALIBRATION")  # type: ignore

        with nav(), div(cls="container"), ul():  # type: ignore
            li(a("Home", href="/html/"))  # type: ignore
            li(a("Topics", href="/html/topics/"))  # type: ignore
            li(a("Posts", href="/html/posts/"))  # type: ignore

            # Check if user exists and render appropriate navigation links
            if user is not None:
                li(a("Profile", href="/html/profile/"))  # type: ignore
                li(a("Logout", href="/html/auth/logout/"))  # type: ignore
            else:
                li(a("Login", href="/html/auth/login/"))  # type: ignore
                li(a("Register", href="/html/auth/register/"))  # type: ignore

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
