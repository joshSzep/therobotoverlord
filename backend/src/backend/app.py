import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.db import init_tortoise
from backend.routes import router
from backend.tasks.session import run_session_cleanup_task
from backend.utils.settings import settings
from backend.utils.version import get_version


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan handler for the FastAPI application."""
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

# Initialize Tortoise ORM
init_tortoise(app)

# Include routers
app.include_router(router)
