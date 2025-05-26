from fastapi import APIRouter

from backend.routes.tags.tags import router as tags_router

router = APIRouter()
router.include_router(tags_router)
