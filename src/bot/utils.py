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


def escape_md_v2(text: str) -> str:
    """Escape all special characters for Telegram MarkdownV2.

    Must escape: _ * [ ] ( ) ~ ` > # + - = | { } . ! and backslash itself.
    """
    if text is None:
        return ""
    # Escape backslash first
    escaped = text.replace("\\", "\\\\")
    specials = r"_*[]()~`>#+-=|{}.!"
    result_chars: list[str] = []
    for ch in escaped:
        if ch in specials:
            result_chars.append("\\" + ch)
        else:
            result_chars.append(ch)
    return "".join(result_chars)


def split_into_chunks(text: str, limit: int = 3900) -> list[str]:
    """Split text into chunks under Telegram's 4096 char limit.

    Attempts to split on newline boundaries, falling back to hard split.
    """
    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        # Try to split at last newline within limit
        split_at = remaining.rfind("\n", 0, limit)
        if split_at == -1 or split_at < limit * 0.5:
            split_at = limit
        chunk = remaining[:split_at]
        chunks.append(chunk)
        remaining = remaining[split_at:].lstrip("\n")
    return chunks
