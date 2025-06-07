# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.auth.login import router as login_router
from backend.routes.html.auth.logout import router as logout_router
from backend.routes.html.auth.register import router as register_router

# Create router
router = APIRouter(prefix="/auth")

# Include route handlers
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(register_router)
