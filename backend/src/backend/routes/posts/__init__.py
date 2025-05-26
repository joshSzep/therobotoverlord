from fastapi import APIRouter

from backend.routes.posts.posts import router as posts_router

router = APIRouter()
router.include_router(posts_router)
