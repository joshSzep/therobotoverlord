# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.users.auth import router as auth_router
from backend.routes.users.profile import router as profile_router

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

router.include_router(auth_router)
router.include_router(profile_router)
