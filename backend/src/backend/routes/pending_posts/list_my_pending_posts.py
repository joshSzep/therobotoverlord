from fastapi import Depends
from fastapi import Query

from backend.db.models.user import User
from backend.db_functions.pending_posts.list_pending_posts import list_pending_posts
from backend.routes.pending_posts import router
from backend.schemas.pending_post import PendingPostList
from backend.utils.auth import get_current_user


@router.get("/my/", response_model=PendingPostList)
async def list_my_pending_posts(
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PendingPostList:
    """
    List the current user's pending posts awaiting moderation.
    """
    return await list_pending_posts(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
