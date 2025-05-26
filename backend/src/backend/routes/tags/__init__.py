# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.routes.tags.create_tag import router as create_tag_router
from backend.routes.tags.delete_tag import router as delete_tag_router
from backend.routes.tags.get_tag import router as get_tag_router
from backend.routes.tags.list_tags import router as list_tags_router
from backend.routes.tags.update_tag import router as update_tag_router

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)

router.include_router(list_tags_router)
router.include_router(create_tag_router)
router.include_router(get_tag_router)
router.include_router(update_tag_router)
router.include_router(delete_tag_router)
