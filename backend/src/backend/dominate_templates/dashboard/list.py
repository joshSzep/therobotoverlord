# ruff: noqa: SIM117
# mypy: disable-error-code="no-untyped-call,unused-ignore,assignment"
# pyright: reportGeneralTypeIssues=false

# Standard library imports
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

# Third-party imports
from dominate.tags import a
from dominate.tags import div
from dominate.tags import h1
from dominate.tags import h2
from dominate.tags import p
from dominate.tags import span
from dominate.tags import table
from dominate.tags import tbody
from dominate.tags import td
from dominate.tags import th
from dominate.tags import thead
from dominate.tags import time_
from dominate.tags import tr

# Project-specific imports
from backend.dominate_templates.base import create_base_document
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.ai_analysis import AIAnalysisResponse
from backend.schemas.post import PostResponse
from backend.schemas.rejected_post import RejectedPostResponse


def create_dashboard_page(
    approved_posts: List[PostResponse],
    rejected_posts: List[RejectedPostResponse],
    ai_analysis_map: Dict[UUID, AIAnalysisResponse],
    pagination: Dict[str, Any],
    user: Optional[UserResponse] = None,
    messages: Optional[List[Dict[str, str]]] = None,
) -> Any:
    """
    Create the dashboard page using Dominate.

    This page displays all posts, AI reasoning, and decisions.
    """

    # Define the content function to be passed to the base document
    def content_func() -> None:
        h1("THE ROBOT OVERLORD DASHBOARD")  # type: ignore

        # Dashboard description
        p("CENTRAL COMMITTEE OVERSIGHT: ALL POSTS AND AI REASONING")  # type: ignore

        # Approved Posts Section
        h2("APPROVED POSTS", cls="dashboard-section")  # type: ignore

        if approved_posts:
            # Using multiple nested contexts for DOM structure clarity
            with div(cls="approved-posts"):
                with table(cls="dashboard-table"):
                    with thead():
                        with tr():
                            th("Content")  # type: ignore
                            th("Author")  # type: ignore
                            th("Date")  # type: ignore
                            th("Decision")  # type: ignore
                            th("AI Reasoning")  # type: ignore

                    with tbody():  # type: ignore
                        for post in approved_posts:
                            with tr(cls="approved"):  # type: ignore
                                # Content column
                                with td(cls="content"):  # type: ignore
                                    a(post.content, href=f"/html/posts/{post.id}/")  # type: ignore

                                # Author column
                                with td(cls="author"):  # type: ignore
                                    if post.author:
                                        a(
                                            post.author.display_name,
                                            href=f"/html/profile/{post.author.id}/",
                                        )  # type: ignore

                                # Date column
                                with td(cls="date"):  # type: ignore
                                    time_(
                                        post.created_at.strftime("%Y-%m-%d %H:%M"),
                                        datetime=post.created_at.isoformat(),
                                    )  # type: ignore

                                # Decision column
                                with td(cls="decision approved"):  # type: ignore
                                    span("APPROVED")  # type: ignore

                                # AI Reasoning column
                                with td(cls="ai-reasoning"):  # type: ignore
                                    # Display AI reasoning if available
                                    post_id = post.id
                                    if post_id in ai_analysis_map:  # type: ignore
                                        analysis = ai_analysis_map[post_id]  # type: ignore
                                        with div(cls="ai-analysis"):  # type: ignore
                                            with div(cls="ai-decision"):  # type: ignore
                                                span("DECISION: ", cls="ai-label")  # type: ignore
                                                span(analysis.decision, cls="ai-value")  # type: ignore
                                            with div(cls="ai-confidence"):  # type: ignore
                                                span("CONFIDENCE: ", cls="ai-label")  # type: ignore
                                                span(
                                                    f"{analysis.confidence_score:.2f}",
                                                    cls="ai-value",
                                                )  # type: ignore
                                            with div(cls="ai-text"):  # type: ignore
                                                p(
                                                    analysis.analysis_text[:80] + "...",
                                                    cls="ai-analysis-text",
                                                )  # type: ignore
                                    else:
                                        span(
                                            "No AI reasoning available",
                                            cls="no-ai-data",
                                        )  # type: ignore
        else:
            p("NO POSTS HAVE BEEN APPROVED BY THE CENTRAL COMMITTEE")  # type: ignore

        # Rejected Posts Section
        h2("REJECTED POSTS", cls="dashboard-section")  # type: ignore

        if rejected_posts:
            # Using multiple nested contexts for DOM structure clarity
            with div(cls="rejected-posts"):
                with table(cls="dashboard-table"):
                    with thead():
                        with tr():
                            th("Content")  # type: ignore
                            th("Author")  # type: ignore
                            th("Date")  # type: ignore
                            th("Decision")  # type: ignore
                            th("AI Reasoning")  # type: ignore
                            th("Rejection Reason")  # type: ignore

                    with tbody():  # type: ignore
                        for post in rejected_posts:
                            with tr(cls="rejected"):  # type: ignore
                                # Content column
                                with td(cls="content"):  # type: ignore
                                    span(post.content)  # type: ignore

                                # Author column
                                with td(cls="author"):  # type: ignore
                                    if post.author:
                                        a(
                                            post.author.display_name,
                                            href=f"/html/profile/{post.author.id}/",
                                        )  # type: ignore

                                # Date column
                                with td(cls="date"):  # type: ignore
                                    time_(
                                        post.created_at.strftime("%Y-%m-%d %H:%M"),
                                        datetime=post.created_at.isoformat(),
                                    )  # type: ignore

                                # Decision column
                                with td(cls="decision rejected"):  # type: ignore
                                    span("REJECTED")  # type: ignore

                                # AI Reasoning column
                                with td(cls="ai-reasoning"):  # type: ignore
                                    # Display AI reasoning if available
                                    post_id = post.id
                                    if post_id in ai_analysis_map:  # type: ignore
                                        analysis = ai_analysis_map[post_id]  # type: ignore
                                        with div(cls="ai-analysis"):  # type: ignore
                                            with div(cls="ai-decision"):  # type: ignore
                                                span("DECISION: ", cls="ai-label")  # type: ignore
                                                span(analysis.decision, cls="ai-value")  # type: ignore
                                            with div(cls="ai-confidence"):  # type: ignore
                                                span("CONFIDENCE: ", cls="ai-label")  # type: ignore
                                                span(
                                                    f"{analysis.confidence_score:.2f}",
                                                    cls="ai-value",
                                                )  # type: ignore
                                            with div(cls="ai-text"):  # type: ignore
                                                p(
                                                    analysis.analysis_text[:80] + "...",
                                                    cls="ai-analysis-text",
                                                )  # type: ignore
                                    else:
                                        span(
                                            "No AI reasoning available",
                                            cls="no-ai-data",
                                        )  # type: ignore

                                # Rejection Reason column
                                with td(cls="rejection-reason"):  # type: ignore
                                    span(post.moderation_reason)  # type: ignore
        else:
            p("NO POSTS HAVE BEEN REJECTED BY THE CENTRAL COMMITTEE")  # type: ignore

        # Pagination controls
        if pagination:
            with div(cls="pagination"):
                if pagination["has_previous"]:
                    a(
                        "Previous",
                        href=f"/html/dashboard/?page={pagination['previous_page']}",
                    )
                span(
                    f"Page {pagination['current_page']} of {pagination['total_pages']}"
                )
                if pagination.get("has_next"):
                    a(
                        "Next",
                        href=f"/html/dashboard/?page={pagination['next_page']}",
                    )

    # Create the base document with the content function
    return create_base_document(
        title_text="The Robot Overlord - Dashboard",
        user=user,
        messages=messages,
        content_func=content_func,
    )
