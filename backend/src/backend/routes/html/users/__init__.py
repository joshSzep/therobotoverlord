from fastapi import APIRouter

from backend.routes.html.users.list_users import router as list_users_router

router = APIRouter()
router.include_router(list_users_router)
