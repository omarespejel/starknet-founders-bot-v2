"""Utility functions for the bot."""

from datetime import datetime, timedelta
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 30, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.requests: Dict[str, List[datetime]] = {}

    def is_allowed(self, user_id: str) -> tuple[bool, str]:
        """Check if user is within rate limits."""
        now = datetime.now()
        user_id = str(user_id)

        # Clean old requests
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time
                for req_time in self.requests[user_id]
                if now - req_time < self.window
            ]
        else:
            self.requests[user_id] = []

        # Check limit
        request_count = len(self.requests[user_id])
        if request_count >= self.max_requests:
            wait_time = self.window - (now - self.requests[user_id][0])
            minutes = int(wait_time.total_seconds() / 60)
            return False, f"Rate limit reached. Please wait {minutes} minutes."

        # Allow request
        self.requests[user_id].append(now)
        return True, ""


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=30, window_minutes=60)


def normalize_query(text: str | None) -> str:
    """Normalize a user query for analytics grouping and reduced PII.

    - Trim and lowercase
    - Collapse whitespace
    - Truncate to 300 chars
    """
    if not text:
        return ""
    normalized = text.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized[:300]
