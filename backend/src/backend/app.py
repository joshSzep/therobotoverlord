# Standard library imports
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI

# Project-specific imports
from backend.db import init_tortoise
from backend.routes import router
from backend.tasks.session import run_session_cleanup_task
from backend.utils.ai_moderation import init_ai_moderator_service
from backend.utils.settings import settings
from backend.utils.version import get_version


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Initialize AI moderation service
    init_ai_moderator_service()

    if not settings.TESTING:
        asyncio.create_task(run_session_cleanup_task())
    yield


app = FastAPI(
    title="The Robot Overlord API",
    description="Backend API for The Robot Overlord",
    version=get_version(),
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Initialize database
init_tortoise(app)

# Include main router
app.include_router(router)
