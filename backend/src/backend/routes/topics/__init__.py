# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.topics.add_topic_tag import router as add_topic_tag_router
from backend.routes.topics.create_topic import router as create_topic_router
from backend.routes.topics.debug_topics import router as debug_topics_router
from backend.routes.topics.delete_topic import router as delete_topic_router
from backend.routes.topics.get_topic import router as get_topic_router
from backend.routes.topics.list_topic_posts import router as list_topic_posts_router
from backend.routes.topics.list_topics import router as list_topics_router
from backend.routes.topics.update_topic import router as update_topic_router

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
)

router.include_router(list_topics_router)
router.include_router(create_topic_router)
router.include_router(get_topic_router)
router.include_router(update_topic_router)
router.include_router(delete_topic_router)
router.include_router(list_topic_posts_router)
router.include_router(add_topic_tag_router)
router.include_router(debug_topics_router)
