from fastapi import APIRouter

from backend.routes.topics.topics import router as topics_router

router = APIRouter()
router.include_router(topics_router)
