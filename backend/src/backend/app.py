import asyncio

from fastapi import FastAPI

from backend.db import init_tortoise
from backend.routes import router
from backend.tasks.session import run_session_cleanup_task
from backend.utils.settings import settings
from backend.utils.version import get_version

app = FastAPI(
    title="The Robot Overlord API",
    description="Backend API for The Robot Overlord",
    version=get_version(),
    debug=settings.DEBUG,
)

# Initialize Tortoise ORM
init_tortoise(app)

# Include routers
app.include_router(router)


# Background task for session cleanup
@app.on_event("startup")
def start_session_cleanup() -> None:
    """Start the background task for cleaning up expired sessions."""
    if not settings.TESTING:
        asyncio.create_task(run_session_cleanup_task())
