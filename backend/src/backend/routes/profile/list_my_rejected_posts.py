from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from backend.db.models.user import User
from backend.db_functions.rejected_posts.list_rejected_posts import list_rejected_posts
from backend.routes.profile import router
from backend.schemas.rejected_post import RejectedPostList
from backend.utils.auth import get_current_user


@router.get("/rejected/", response_model=RejectedPostList)
async def list_my_rejected_posts(
    current_user: User | None = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> RejectedPostList:
    """
    List the current user's rejected posts with moderation feedback.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    rejected_posts_list = await list_rejected_posts(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    # Get the count of rejected posts
    posts_count = rejected_posts_list.count if rejected_posts_list else 0

    # Create the response with the list of rejected posts
    return RejectedPostList(
        rejected_posts=rejected_posts_list.rejected_posts, count=posts_count
    )
