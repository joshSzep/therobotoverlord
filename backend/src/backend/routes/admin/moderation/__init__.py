from fastapi import APIRouter

from backend.routes.admin.moderation.dashboard import router as dashboard_router
from backend.routes.admin.moderation.pending_posts import router as pending_posts_router

router = APIRouter()

router.include_router(
    dashboard_router, prefix="/dashboard", tags=["admin", "moderation"]
)
router.include_router(
    pending_posts_router, prefix="/pending-posts", tags=["admin", "moderation"]
)
