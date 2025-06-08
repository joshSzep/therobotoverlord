# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.admin import router as admin_router
from backend.routes.api import router as api_router
from backend.routes.auth import router as auth_router
from backend.routes.health import router as health_router
from backend.routes.html import router as html_router
from backend.routes.pending_posts import router as pending_posts_router
from backend.routes.posts import router as posts_router
from backend.routes.profile import router as profile_router
from backend.routes.tags import router as tags_router
from backend.routes.topics import router as topics_router
from backend.routes.user_stats import router as user_stats_router

# Create main router
router = APIRouter()

# Include all feature routers
router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(topics_router)
router.include_router(tags_router)
router.include_router(posts_router)
router.include_router(pending_posts_router)
router.include_router(user_stats_router)
router.include_router(health_router)

# Include API router
router.include_router(api_router, prefix="/api")

# Include admin router
router.include_router(admin_router, prefix="/admin")

# Include HTML template-driven frontend router
router.include_router(html_router)
