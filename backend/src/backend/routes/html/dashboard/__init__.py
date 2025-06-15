# Standard library imports

# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.dashboard.list_dashboard import router as list_dashboard_router

router = APIRouter(prefix="/dashboard")

# Include the list_dashboard router
router.include_router(list_dashboard_router)
