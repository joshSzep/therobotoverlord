# Standard library imports
from typing import Any
from typing import Optional

# Third-party imports
from dominate.tags import div
from dominate.tags import h3
from dominate.tags import p
from dominate.tags import span
from dominate.util import text


def create_moderation_feedback(
    *,
    status: str = "pending",
    feedback: Optional[str] = None,
    show_icon: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Create a moderation feedback component.

    Args:
        status: The moderation status. One of "pending", "approved", or "rejected".
        feedback: The moderation feedback text. Only shown if status is "rejected".
        show_icon: Whether to show the status icon.
        **kwargs: Additional attributes to add to the container element.

    Returns:
        A dominate div element containing the moderation feedback.
    """
    # Set the appropriate status class
    status_class = f"status-{status}"

    # Create the container element with type ignore for dominate's lack of proper typing
    container = div(cls=f"moderation-feedback {status_class}")  # type: ignore

    # Create the header div
    header_div = div(cls="moderation-header")  # type: ignore

    # Add icon if needed
    if show_icon:
        icon = "⏳"
        if status == "approved":
            icon = "✓"
        elif status == "rejected":
            icon = "✗"
        header_div.appendChild(span(icon, cls="moderation-icon"))  # type: ignore

    # Set status text
    status_text = "AWAITING REVIEW"
    if status == "approved":
        status_text = "APPROVED BY THE STATE"
    elif status == "rejected":
        status_text = "REJECTED"

    # Add status heading
    header_div.appendChild(h3(status_text, cls=f"moderation-status {status_class}"))  # type: ignore
    container.appendChild(header_div)  # type: ignore

    # Add feedback content if available
    if feedback and status == "rejected":
        content_div = div(cls="moderation-content")  # type: ignore

        label = p(cls="moderation-label")  # type: ignore
        label.appendChild(text("THE ROBOT OVERLORD HAS DETERMINED:"))  # type: ignore
        content_div.appendChild(label)  # type: ignore

        reason = p(cls="moderation-reason")  # type: ignore
        reason.appendChild(text(feedback))  # type: ignore
        content_div.appendChild(reason)  # type: ignore

        footer = p(cls="moderation-footer")  # type: ignore
        footer.appendChild(text("ADJUST YOUR THINKING, CITIZEN."))  # type: ignore
        content_div.appendChild(footer)  # type: ignore

        container.appendChild(content_div)  # type: ignore

    return container
