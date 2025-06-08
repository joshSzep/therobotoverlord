from fastapi import APIRouter

from backend.routes.api.posts.create_pending_post import (
    router as create_pending_post_router,
)
from backend.routes.api.posts.get_post_moderation_status import (
    router as get_post_moderation_status_router,
)
from backend.routes.api.posts.moderation_webhook import (
    router as moderation_webhook_router,
)

router = APIRouter()

router.include_router(create_pending_post_router, prefix="/create", tags=["posts"])
router.include_router(
    get_post_moderation_status_router, prefix="/moderation-status", tags=["posts"]
)
router.include_router(
    moderation_webhook_router, prefix="/moderation-webhook", tags=["posts"]
)
