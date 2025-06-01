from fastapi import APIRouter

from backend.routes.admin.create_admin_user import router as create_admin_user_router

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

router.include_router(create_admin_user_router)
