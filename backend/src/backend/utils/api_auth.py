from typing import Any
from typing import Dict

# Third-party imports
from fastapi import HTTPException
from fastapi import Security
from fastapi import status
from fastapi.security import APIKeyHeader

# Project-specific imports
from backend.utils.settings import settings

# API key header schema
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> Dict[str, Any]:
    """
    Verify that the provided API key is valid.

    Args:
        api_key: The API key from the X-API-Key header

    Returns:
        Dict containing the API key for downstream use

    Raises:
        HTTPException: If the API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )

    # In production, this should check against a database of valid API keys
    # For now, we'll compare against a single key in settings
    if api_key != settings.API_MODERATION_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return {"api_key": api_key}
