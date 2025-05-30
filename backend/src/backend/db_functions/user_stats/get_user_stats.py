from uuid import UUID

from backend.db.models.pending_post import PendingPost
from backend.db.models.post import Post
from backend.db.models.rejected_post import RejectedPost
from backend.db.models.user import User
from backend.schemas.user_stats import UserStatsResponse


async def get_user_stats(user_id: UUID) -> UserStatsResponse:
    """
    Get a user's post statistics including approved, rejected, and pending counts.
    """
    # Get the user
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Count approved posts
    approved_count = await Post.filter(author_id=user_id).count()

    # Count rejected posts
    rejected_count = await RejectedPost.filter(author_id=user_id).count()

    # Count pending posts
    pending_count = await PendingPost.filter(author_id=user_id).count()

    # Calculate approval rate
    total_decisions = approved_count + rejected_count
    approval_rate = (
        (approved_count / total_decisions) * 100 if total_decisions > 0 else 0
    )

    return UserStatsResponse(
        user_id=user_id,
        username=user.display_name,
        approved_count=approved_count,
        rejected_count=rejected_count,
        pending_count=pending_count,
        approval_rate=approval_rate,
    )
