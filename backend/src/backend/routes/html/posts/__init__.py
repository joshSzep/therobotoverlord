# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.posts.create_post import router as create_post_router
from backend.routes.html.posts.get_post import router as get_post_router
from backend.routes.html.posts.list_posts import router as list_posts_router

# Create router
router = APIRouter(prefix="/posts")

# Include route handlers
router.include_router(list_posts_router)
router.include_router(get_post_router)
router.include_router(create_post_router)
