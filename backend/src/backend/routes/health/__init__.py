from fastapi import APIRouter

from backend.routes.health.check import router as check_router
from backend.routes.health.heartbeat import router as heartbeat_router

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

router.include_router(check_router)
router.include_router(heartbeat_router)
