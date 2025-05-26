from fastapi import APIRouter

from backend.routes.health import router as health_router
from backend.routes.posts import router as posts_router
from backend.routes.tags import router as tags_router
from backend.routes.topics import router as topics_router
from backend.routes.users import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(topics_router, prefix="/topics", tags=["topics"])
router.include_router(tags_router, prefix="/tags", tags=["tags"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(health_router)
