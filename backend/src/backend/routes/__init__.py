# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.auth import router as auth_router
from backend.routes.health import router as health_router
from backend.routes.posts import router as posts_router
from backend.routes.profile import router as profile_router
from backend.routes.tags import router as tags_router
from backend.routes.topics import router as topics_router

# Create main router
router = APIRouter()

# Include all feature routers
router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(topics_router)
router.include_router(tags_router)
router.include_router(posts_router)
router.include_router(health_router)
