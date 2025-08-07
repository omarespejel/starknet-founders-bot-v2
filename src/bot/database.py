"""Database operations using Supabase."""

import logging
import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    """Handle all database operations."""

    def __init__(self) -> None:
        self.client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY"),
        )

    async def save_message(
        self,
        user_id: str,
        username: str | None,
        first_name: str | None,
        agent_type: str,
        role: str,
        message: str,
        tokens_used: int = 0,
    ) -> dict:
        """Save a message to the database."""
        try:
            result = (
                self.client.table("conversations")
                .insert(
                    {
                        "user_id": user_id,
                        "username": username,
                        "first_name": first_name,
                        "agent_type": agent_type,
                        "role": role,
                        "message": message,
                        "tokens_used": tokens_used,
                    },
                )
                .execute()
            )
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise

    async def get_conversation_history(
        self,
        user_id: str,
        agent_type: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get recent conversation history."""
        try:
            result = (
                self.client.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .eq("agent_type", agent_type)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            # Return in chronological order
            return list(reversed(result.data)) if result.data else []
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def update_user_session(
        self,
        user_id: str,
        username: str | None,
        first_name: str | None,
        agent_type: str,
    ) -> None:
        """Update or create user session."""
        try:
            # Upsert user session
            self.client.table("user_sessions").upsert(
                {
                    "user_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "current_agent": agent_type,
                    "last_active": datetime.now(UTC).isoformat(),
                },
            ).execute()
        except Exception as e:
            logger.error(f"Error updating user session: {e}")

    async def clear_conversation(
        self,
        user_id: str,
        agent_type: str | None = None,
    ) -> None:
        """Clear conversation history for a user."""
        try:
            query = self.client.table("conversations").delete().eq("user_id", user_id)

            if agent_type:
                query = query.eq("agent_type", agent_type)

            query.execute()
            logger.info(f"Cleared conversations for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing conversations: {e}")

    async def get_user_stats(self, user_id: str) -> dict:
        """Get user statistics."""
        try:
            # Get message counts
            total_messages = (
                self.client.table("conversations")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("role", "user")
                .execute()
            )

            pm_messages = (
                self.client.table("conversations")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("agent_type", "pm")
                .eq("role", "user")
                .execute()
            )

            vc_messages = (
                self.client.table("conversations")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("agent_type", "vc")
                .eq("role", "user")
                .execute()
            )

            # Get first message date
            first_message = (
                self.client.table("conversations")
                .select("created_at")
                .eq("user_id", user_id)
                .order("created_at")
                .limit(1)
                .execute()
            )

            return {
                "total_messages": total_messages.count or 0,
                "pm_messages": pm_messages.count or 0,
                "vc_messages": vc_messages.count or 0,
                "first_message_date": (
                    first_message.data[0]["created_at"] if first_message.data else None
                ),
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_messages": 0,
                "pm_messages": 0,
                "vc_messages": 0,
                "first_message_date": None,
            }
