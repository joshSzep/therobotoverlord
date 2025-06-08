from fastapi import APIRouter

# Import routers from route files
from backend.routes.html.pending_posts.get_pending_post import (
    router as get_pending_post_router,
)
from backend.routes.html.pending_posts.list_pending_posts import (
    router as list_pending_posts_router,
)
from backend.routes.html.pending_posts.moderate_pending_post import (
    router as moderate_pending_post_router,
)

# Create main router for the pending posts module
router = APIRouter(
    prefix="/pending-posts",
    tags=["html_pending_posts"],
)

# Include all route handlers
router.include_router(list_pending_posts_router)
router.include_router(get_pending_post_router)
router.include_router(moderate_pending_post_router)

# Export public API
__all__ = [
    "router",
]
