from fastapi import APIRouter

from backend.routes.api.topics.debug_topics import router as debug_topics_router

router = APIRouter()

router.include_router(debug_topics_router, prefix="/debug", tags=["topics"])
