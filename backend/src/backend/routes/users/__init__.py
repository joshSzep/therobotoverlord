from fastapi import APIRouter

from backend.routes.users import auth
from backend.routes.users import profile

router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(profile.router, prefix="/profile")
