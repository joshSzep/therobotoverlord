# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.topics.create_topic import router as create_topic_router
from backend.routes.topics.delete_topic import router as delete_topic_router
from backend.routes.topics.get_topic import router as get_topic_router
from backend.routes.topics.list_topics import router as list_topics_router
from backend.routes.topics.update_topic import router as update_topic_router

router = APIRouter(tags=["topics"])

router.include_router(list_topics_router)
router.include_router(create_topic_router)
router.include_router(get_topic_router)
router.include_router(update_topic_router)
router.include_router(delete_topic_router)
