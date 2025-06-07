from tortoise.exceptions import ConfigurationError

from backend.db.models.post import Post
from backend.db.models.user import User
from backend.schemas.user import UserSchema


async def user_to_schema(user: User) -> UserSchema:
    # Count approved posts
    approved_count = await Post.filter(author_id=user.id).count()

    # Count rejected posts - safely handle if the model isn't configured
    rejected_count = 0
    try:
        # Import here to avoid circular imports
        from backend.db.models.rejected_post import RejectedPost

        rejected_count = await RejectedPost.filter(author_id=user.id).count()
    except ConfigurationError:
        # Model not properly configured, use 0 as fallback
        pass

    return UserSchema(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_verified=user.is_verified,
        role=user.role,
        is_locked=user.is_locked,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        approved_count=approved_count,
        rejected_count=rejected_count,
    )
