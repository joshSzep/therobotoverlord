from fastapi import APIRouter

# Import subrouters from each route module
from backend.routes.pending_posts.approve_pending_post import router as approve_router
from backend.routes.pending_posts.create_pending_post import router as create_router
from backend.routes.pending_posts.list_my_pending_posts import router as list_my_router
from backend.routes.pending_posts.list_pending_posts import router as list_router
from backend.routes.pending_posts.reject_pending_post import router as reject_router

# Create the main pending posts router
router = APIRouter(prefix="/pending-posts", tags=["pending-posts"])

# Include all subrouters
router.include_router(approve_router, prefix="")
router.include_router(create_router, prefix="")
router.include_router(list_my_router, prefix="")
router.include_router(list_router, prefix="")
router.include_router(reject_router, prefix="")
