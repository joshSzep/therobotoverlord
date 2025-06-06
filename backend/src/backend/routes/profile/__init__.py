# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.profile.change_password import router as change_password_router
from backend.routes.profile.get_me import router as get_me_router
from backend.routes.profile.logout import router as logout_router

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)

router.include_router(get_me_router)
router.include_router(change_password_router)
router.include_router(logout_router)
