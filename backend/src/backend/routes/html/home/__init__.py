# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.home.index import router as index_router

# Create router
router = APIRouter()

# Include routes
router.include_router(index_router)
