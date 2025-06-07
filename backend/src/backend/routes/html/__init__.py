# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.auth import router as auth_router
from backend.routes.html.posts import router as posts_router
from backend.routes.html.profile import router as profile_router
from backend.routes.html.root import router as root_router
from backend.routes.html.topics import router as topics_router

# Create HTML router
router = APIRouter(prefix="/html")

# Include all HTML feature routers
# Include the root router first to handle the /html/ path
router.include_router(root_router)
router.include_router(topics_router)
router.include_router(posts_router)
router.include_router(profile_router)
router.include_router(auth_router)
