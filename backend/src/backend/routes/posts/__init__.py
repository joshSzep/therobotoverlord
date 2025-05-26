# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.posts.create_post import router as create_post_router
from backend.routes.posts.delete_post import router as delete_post_router
from backend.routes.posts.get_post import router as get_post_router
from backend.routes.posts.list_post_replies import router as list_post_replies_router
from backend.routes.posts.list_posts import router as list_posts_router
from backend.routes.posts.list_topic_posts import router as list_topic_posts_router
from backend.routes.posts.update_post import router as update_post_router

router = APIRouter(tags=["posts"])

router.include_router(list_posts_router)
router.include_router(create_post_router)
router.include_router(get_post_router)
router.include_router(update_post_router)
router.include_router(delete_post_router)
router.include_router(list_topic_posts_router)
router.include_router(list_post_replies_router)
