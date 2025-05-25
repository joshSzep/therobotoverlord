from fastapi import APIRouter

from backend.routes.health import router as health_router
from backend.routes.users import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(health_router)
