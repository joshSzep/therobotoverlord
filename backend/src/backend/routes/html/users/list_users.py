# Third-party imports
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse

# Project-specific imports
from backend.db_functions.users.list_users import list_users
from backend.dominate_templates.users import users_page
from backend.routes.html.utils.auth import get_current_user_optional
from backend.schemas.user import UserSchema

router = APIRouter()


@router.get("/users/", response_class=HTMLResponse)
async def list_users_route(
    request: Request,
    current_user: UserSchema = Depends(get_current_user_optional),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> HTMLResponse:
    # Calculate skip for pagination
    skip = (page - 1) * limit

    # Get users with pagination
    users, total_count = await list_users(skip=skip, limit=limit)

    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit

    # Render the HTML page
    html = users_page(
        request=request,
        current_user=current_user,
        users=users,
        page=page,
        total_pages=total_pages,
        total_count=total_count,
    )

    return HTMLResponse(content=html)
