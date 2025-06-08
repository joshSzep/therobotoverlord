from fastapi import APIRouter

# Import routers from route files
from backend.routes.html.rejected_posts.get_rejected_post import (
    router as get_rejected_post_router,
)
from backend.routes.html.rejected_posts.list_rejected_posts import (
    router as list_rejected_posts_router,
)

# Create main router for the rejected posts module
router = APIRouter(
    prefix="/rejected-posts",
    tags=["html_rejected_posts"],
)

# Include all route handlers
router.include_router(list_rejected_posts_router)
router.include_router(get_rejected_post_router)

# Export public API
__all__ = [
    "router",
]
