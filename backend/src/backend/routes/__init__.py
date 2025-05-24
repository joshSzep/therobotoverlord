from fastapi import APIRouter

from backend.routes.health import router as health_router

router = APIRouter()
router.include_router(health_router)
