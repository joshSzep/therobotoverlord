# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.html.topics.get_topic import router as get_topic_router
from backend.routes.html.topics.list_topics import router as list_topics_router

# Create router
router = APIRouter(prefix="/topics")

# Include route handlers
router.include_router(list_topics_router)
router.include_router(get_topic_router)
