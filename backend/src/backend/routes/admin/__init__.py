from fastapi import APIRouter

from backend.routes.admin.moderation import router as moderation_router

router = APIRouter()

router.include_router(
    moderation_router, prefix="/moderation", tags=["admin", "moderation"]
)
