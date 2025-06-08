from fastapi import APIRouter

from backend.routes.api.posts import router as posts_router
from backend.routes.api.topics import router as topics_router

router = APIRouter()

router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(topics_router, prefix="/topics", tags=["topics"])
