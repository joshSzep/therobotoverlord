# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.users.auth.login import router as login_router
from backend.routes.users.auth.refresh_token import router as refresh_token_router
from backend.routes.users.auth.register import router as register_router

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

router.include_router(login_router)
router.include_router(register_router)
router.include_router(refresh_token_router)
