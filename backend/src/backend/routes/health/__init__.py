# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.health.health import router as health_router
from backend.routes.health.heartbeat import router as heartbeat_router
from backend.routes.health.trigger_500_error import router as trigger_500_error_router

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

router.include_router(health_router)
router.include_router(heartbeat_router)
router.include_router(trigger_500_error_router)
