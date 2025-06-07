# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

# Third-party imports
from dominate.tags import a
from dominate.tags import button
from dominate.tags import div
from dominate.tags import form
from dominate.tags import h1
from dominate.tags import input_
from dominate.tags import label
from dominate.tags import p
from dominate.util import text

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse


def create_login_page(
    user: Optional[Union[UserResponse, Dict[str, Any]]] = None,
    messages: Optional[List[Dict[str, str]]] = None,
) -> Any:
    """
    Create the login page using Dominate.

    Args:
        user: User schema object or dictionary
        messages: List of message dictionaries

    Returns:
        A dominate document object
    """
    # Define the content function to be passed to the base document

    # Define the content function to be passed to the base document
    def content_func() -> None:
        with div(cls="auth-container"):  # type: ignore
            h1("CITIZEN IDENTIFICATION")  # type: ignore

            with form(action="/html/auth/login/", method="post", cls="auth-form"):  # type: ignore
                with div(cls="form-group"):  # type: ignore
                    label("Email:", for_="email")  # type: ignore
                    input_(type="email", id="email", name="email", required=True)  # type: ignore

                with div(cls="form-group"):  # type: ignore
                    label("Password:", for_="password")  # type: ignore
                    input_(
                        type="password", id="password", name="password", required=True
                    )  # type: ignore

                button("AUTHENTICATE", type="submit")  # type: ignore

            with div(cls="auth-links"), p():  # type: ignore
                text("Not registered? ")  # type: ignore
                a("Register here", href="/html/auth/register/")  # type: ignore

    # Create the base document with the content function
    return create_base_document(
        title_text="Login - The Robot Overlord",
        user=user,
        messages=messages,
        content_func=content_func,
    )
