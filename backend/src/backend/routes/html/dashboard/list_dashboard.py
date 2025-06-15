# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.db_functions.dashboard.get_dashboard_data import get_dashboard_data
from backend.dominate_templates.dashboard.list import create_dashboard_page
from backend.routes.html.schemas.user import UserResponse
from backend.routes.html.utils.auth import get_current_user_optional

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_dashboard_page(
    request: Request,
    current_user: Annotated[UserResponse | None, Depends(get_current_user_optional)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> HTMLResponse:
    # Calculate skip value for pagination
    skip = (page - 1) * limit

    # Get dashboard data with pagination
    # (approved posts, rejected posts, and AI analysis)
    (
        approved_posts_data,
        rejected_posts_data,
        ai_analysis_map,
    ) = await get_dashboard_data(skip=skip, limit=limit)

    # Extract posts and counts
    approved_posts = approved_posts_data.posts
    approved_total = approved_posts_data.count
    rejected_posts = rejected_posts_data.rejected_posts
    rejected_total = rejected_posts_data.count

    # Combine all posts for the dashboard
    total_count = approved_total + rejected_total
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1

    # Create pagination data
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "previous_page": page - 1,
        "next_page": page + 1,
    }

    # Create the dashboard page using Dominate
    doc = create_dashboard_page(
        approved_posts=approved_posts,
        rejected_posts=rejected_posts,
        ai_analysis_map=ai_analysis_map,
        pagination=pagination,
        user=current_user,
    )

    # Return the rendered HTML
    return HTMLResponse(str(doc))
