# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.profile.index import router as profile_index_router

# Create router
router = APIRouter(prefix="/profile")

# Include route handlers
router.include_router(profile_index_router)
