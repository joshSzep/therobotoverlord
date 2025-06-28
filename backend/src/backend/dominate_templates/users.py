# Standard library imports
from typing import Any
from typing import List
from typing import Optional
from typing import cast

# Third-party imports
from dominate.tags import a
from dominate.tags import div
from dominate.tags import h1
from dominate.tags import p
from dominate.tags import span
from dominate.tags import table
from dominate.tags import tbody
from dominate.tags import td
from dominate.tags import th
from dominate.tags import thead
from dominate.tags import tr
from dominate.util import text
from fastapi import Request

# Local imports
from backend.dominate_templates.base import create_base_document
from backend.schemas.user import UserSchema
from backend.utils.role_check import is_admin


def users_page(
    request: Request,
    users: List[UserSchema],
    page: int,
    total_pages: int,
    total_count: int,
    current_user: Optional[UserSchema] = None,
) -> str:
    """
    Create the users listing page using Dominate.

    Args:
        request: FastAPI request object
        users: List of UserSchema objects
        page: Current page number
        total_pages: Total number of pages
        total_count: Total number of users
        current_user: Optional UserSchema object for the current logged-in user

    Returns:
        HTML string for the users page
    """

    def content_func() -> None:
        # Page header
        with div(cls="users-header"):  # type: ignore
            h1("CITIZEN REGISTRY")  # type: ignore
            p(f"DISPLAYING {len(users)} OF {total_count} REGISTERED CITIZENS")  # type: ignore

        # Check if current user is admin
        user_is_admin = current_user and is_admin(current_user.role)

        # Users table
        with div(cls="users-table-container"), table(cls="users-table"):  # type: ignore
            with thead(), tr():  # type: ignore
                th("Display Name")  # type: ignore
                # Only show Email column header for admins
                if user_is_admin:
                    th("Email")  # type: ignore
                th("Role")  # type: ignore
                th("Verified")  # type: ignore
                th("Account Status")  # type: ignore
                th("Approved")  # type: ignore
                th("Rejected")  # type: ignore
                th("Last Login")  # type: ignore

            with tbody():  # type: ignore
                for user in users:
                    with tr():  # type: ignore
                        with td():  # type: ignore
                            a(
                                user.display_name,
                                href=f"/html/profile/{user.id}/",
                                cls="user-profile-link",
                            )  # type: ignore
                        # Only show Email column data for admins
                        if user_is_admin:
                            td(user.email)  # type: ignore
                        td(user.role)  # type: ignore
                        td("✓" if user.is_verified else "✗")  # type: ignore
                        td("Locked" if user.is_locked else "Active")  # type: ignore
                        td(user.approved_count, cls="approved-count")  # type: ignore
                        td(user.rejected_count, cls="rejected-count")  # type: ignore
                        td(
                            user.last_login.strftime("%Y-%m-%d %H:%M")
                            if user.last_login
                            else "Never"
                        )  # type: ignore

        # Pagination
        if total_pages > 1:
            with div(cls="pagination"):  # type: ignore
                if page > 1:
                    a(
                        "← Previous",
                        href=f"/html/users/?page={page - 1}",
                        cls="pagination-link",
                    )  # type: ignore

                with span(cls="pagination-info"):  # type: ignore
                    text(f"Page {page} of {total_pages}")  # type: ignore

                if page < total_pages:
                    a(
                        "Next →",
                        href=f"/html/users/?page={page + 1}",
                        cls="pagination-link",
                    )  # type: ignore

    # Create the document
    doc = create_base_document(
        title_text="User Registry - The Robot Overlord",
        user=cast(Any, current_user),
        content_func=content_func,
    )

    # Return the HTML string
    return str(doc.render())
