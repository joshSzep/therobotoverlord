# Standard library imports
from typing import Dict
from typing import List
from typing import Optional

# Third-party imports
from dominate.tags import a
from dominate.tags import button
from dominate.tags import div
from dominate.tags import form
from dominate.tags import h1
from dominate.tags import input_
from dominate.tags import p
from dominate.tags import span
from dominate.util import text

# Project-specific imports
from backend.dominate_templates.base import create_base_document
from backend.dominate_templates.components.moderation_feedback import (
    create_moderation_feedback,
)
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.pending_post import PendingPostResponse


def create_pending_post_detail_page(
    pending_post: PendingPostResponse,
    user: Optional[UserResponse] = None,
    is_admin: bool = False,
    is_owner: bool = False,
    messages: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Create the pending post detail page using Dominate.

    Args:
        pending_post: PendingPostResponse object
        user: UserResponse object
        is_admin: Whether the current user is an admin
        is_owner: Whether the current user is the owner of the post
        messages: List of message dictionaries

    Returns:
        A dominate document object
    """

    # Helper function to generate moderation URL
    def get_moderation_url(post_id: str) -> str:
        return f"/html/pending-posts/{post_id}/moderate/"

    # Define the content function to be passed to the base document
    def content_func() -> None:
        # Display page title
        h1(f"PENDING POST: {pending_post.title}")  # type: ignore

        with div(cls="pending-post-detail"):  # type: ignore
            # Post content section
            with div(cls="pending-post-content"):  # type: ignore
                # Content
                with div(cls="pending-post-content-text"):  # type: ignore
                    p(pending_post.content)  # type: ignore

                # Post metadata section
                with div(cls="pending-post-meta"):  # type: ignore
                    # Topic info
                    with div(cls="pending-post-topic"):  # type: ignore
                        if hasattr(pending_post, "topic") and pending_post.topic:
                            text("Topic: ")  # type: ignore
                            # Get topic ID safely
                            topic_id = pending_post.topic.get("id", "")
                            topic_url = f"/html/topics/{topic_id}/"
                            a(
                                pending_post.topic.get("title", "Unknown"),
                                href=topic_url,
                                cls="topic-link",
                            )  # type: ignore
                        else:
                            span("No topic", cls="no-topic")  # type: ignore

                    # Author info
                    with div(cls="pending-post-author"):  # type: ignore
                        text("Submitted by: ")  # type: ignore
                        if hasattr(pending_post, "user") and pending_post.user:
                            author_name = getattr(
                                pending_post.user,
                                "display_name",
                                "Unknown",
                            )
                            author_id = getattr(pending_post.user, "id", None)
                            if author_id:
                                href = f"/html/profile/{author_id}/"
                                a(author_name, href=href)  # type: ignore
                            else:
                                text(author_name)  # type: ignore
                        else:
                            text("Unknown")  # type: ignore

                    # Submission date
                    with div(cls="pending-post-date"):  # type: ignore
                        if hasattr(pending_post, "created_at"):
                            text(f"Submitted on: {pending_post.created_at}")  # type: ignore

                # AI moderation status if available
                if hasattr(pending_post, "ai_moderation_status"):
                    with div(cls="ai-moderation-status"):  # type: ignore
                        status = pending_post.ai_moderation_status
                        # Get AI feedback if available
                        feedback = None
                        if (
                            hasattr(pending_post, "ai_feedback")
                            and pending_post.ai_feedback
                        ):
                            feedback = pending_post.ai_feedback

                        # Use our moderation feedback component
                        # Convert status to lowercase safely
                        status_lower = status.lower() if status else "pending"
                        create_moderation_feedback(
                            feedback=feedback,
                            status=status_lower,
                            show_icon=True,
                        )

            # Moderation controls
            if is_admin or is_owner:
                with div(cls="moderation-controls soviet-panel"):  # type: ignore
                    h1("CITIZEN SUBMISSION EVALUATION", cls="soviet-header")  # type: ignore

                    # Approval form with Soviet styling
                    with div(cls="moderation-action approve-action"):  # type: ignore
                        # Use a single with statement for form
                        form_attrs = {
                            "action": get_moderation_url(str(pending_post.id)),
                            "method": "post",
                            "cls": "soviet-form",
                        }
                        with form(**form_attrs):  # type: ignore
                            input_(type="hidden", name="action", value="approve")  # type: ignore
                            button(
                                "APPROVE FOR COLLECTIVE",
                                type="submit",
                                cls="approve-button soviet-button",
                            )  # type: ignore

                    # Rejection form with Soviet styling
                    with div(cls="moderation-action reject-action"):  # type: ignore
                        # Use a single with statement for form
                        form_attrs = {
                            "action": get_moderation_url(str(pending_post.id)),
                            "method": "post",
                            "cls": "soviet-form",
                        }
                        with form(**form_attrs):  # type: ignore
                            input_(type="hidden", name="action", value="reject")  # type: ignore
                            # Shorten placeholder text to fix line length
                            input_(
                                type="text",
                                name="moderation_reason",
                                placeholder="Rejection reason (LOGIC ERROR, IDEOLOGY)",
                                cls="rejection-reason",
                            )  # type: ignore
                            button(
                                "REJECT FOR REEDUCATION",
                                type="submit",
                                cls="reject-button soviet-button",
                            )  # type: ignore

                    # AI Moderation trigger button with Soviet styling
                    if is_admin:  # Only show for admins
                        with div(cls="moderation-action ai-moderation-action"):  # type: ignore
                            # Helper function to generate AI moderation URL
                            def get_ai_moderation_url(post_id: str) -> str:
                                base_url = "/html/pending-posts/"
                                return f"{base_url}{post_id}/trigger-ai-moderation/"

                            form_attrs = {
                                "action": get_ai_moderation_url(str(pending_post.id)),
                                "method": "post",
                                "cls": "soviet-form",
                            }
                            with form(**form_attrs):  # type: ignore
                                button(
                                    "TRIGGER AI MODERATION",
                                    type="submit",
                                    cls="ai-moderation-button soviet-button",
                                )  # type: ignore

        # Back to list link
        with div(cls="back-link"):  # type: ignore
            a("← Back to Pending Posts", href="/html/pending-posts/")  # type: ignore

    # Create the base document with the content function
    return str(
        create_base_document(
            title_text=f"The Robot Overlord - Pending Post: {pending_post.title}",
            user=user,
            messages=messages,
            content_func=content_func,
        )
    )
