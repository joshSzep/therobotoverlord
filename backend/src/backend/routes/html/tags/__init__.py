from fastapi import APIRouter

from backend.routes.html.tags.list_topics_by_tag import router as tag_router

# Create router with prefix
router = APIRouter(prefix="/tags")
router.include_router(tag_router)
