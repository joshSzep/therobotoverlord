# Standard library imports
import time
from typing import Dict
from typing import List
from typing import Tuple

# Third-party imports
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

# Project-specific imports


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""

    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.request_history: Dict[str, List[float]] = {}
        self.window_seconds = 60  # 1 minute window

    def _clean_old_requests(self, client_id: str) -> None:
        """Remove requests older than the window from history."""
        if client_id not in self.request_history:
            return

        current_time = time.time()
        self.request_history[client_id] = [
            timestamp
            for timestamp in self.request_history[client_id]
            if current_time - timestamp < self.window_seconds
        ]

    def check_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if a client has exceeded their rate limit.

        Args:
            client_id: Identifier for the client (IP address, API key, etc.)

        Returns:
            Tuple[bool, int]: (is_allowed, remaining_requests)
        """
        self._clean_old_requests(client_id)

        # Initialize history for new clients
        if client_id not in self.request_history:
            self.request_history[client_id] = []

        # Count recent requests
        recent_requests = len(self.request_history[client_id])

        # Check if limit exceeded
        if recent_requests >= self.requests_per_minute:
            return False, 0

        # Record this request
        self.request_history[client_id].append(time.time())

        # Return allowed with remaining requests
        return True, self.requests_per_minute - recent_requests - 1


# Create global rate limiter instances
moderation_rate_limiter = RateLimiter(requests_per_minute=30)
general_rate_limiter = RateLimiter(requests_per_minute=60)


async def limit_moderation_requests(request: Request) -> None:
    """
    Dependency for rate limiting moderation API requests.

    Args:
        request: The FastAPI request object

    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_id = request.client.host if request.client else "unknown"
    allowed, remaining = moderation_rate_limiter.check_rate_limit(client_id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for moderation requests. Try again later.",
            headers={"X-Rate-Limit-Remaining": "0"},
        )

    # Add rate limit info to response headers
    request.state.rate_limit_remaining = remaining
