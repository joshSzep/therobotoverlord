# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.health.check import router as check_router
from backend.routes.health.heartbeat import router as heartbeat_router

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

router.include_router(check_router)
router.include_router(heartbeat_router)
