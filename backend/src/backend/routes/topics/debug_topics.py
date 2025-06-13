# Standard library imports

# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.db_functions.topics import list_topics
from backend.schemas.topic import TopicList

router = APIRouter()


@router.get("/debug/", response_model=TopicList)
async def debug_topics() -> TopicList:
    """
    Debug endpoint to get all topics with their descriptions and tags.
    """
    return await list_topics(skip=0, limit=100)
