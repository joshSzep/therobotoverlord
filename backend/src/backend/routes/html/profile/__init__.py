# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.profile.get_user_profile import (
    router as get_user_profile_router,
)
from backend.routes.html.profile.index import router as profile_index_router

# Create router
router = APIRouter(prefix="/profile")

# Include route handlers
router.include_router(profile_index_router)
router.include_router(get_user_profile_router)
