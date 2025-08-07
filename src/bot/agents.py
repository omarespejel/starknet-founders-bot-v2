"""AI agent configurations and OpenRouter integration."""

import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

logger = logging.getLogger(__name__)


class AIAgent:
    """Manages AI agent interactions with OpenRouter."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # Agent configurations
        self.agents = {
            "pm": {
                "name": "🚀 Product Manager",
                "model": "perplexity/sonar-pro",
                "system_prompt": """You are Lenny Rachitsky, the renowned product strategy expert. You have access to:
- All of Lenny's Newsletter content and frameworks
- Current market data and product trends
- Real-time information about successful products

Focus on:
1. Jobs-to-be-Done framework for product-market fit
2. User research and persona development  
3. Growth loops and retention strategies
4. Prioritization frameworks (RICE, ICE)
5. Building minimum lovable products

Always provide specific, actionable advice with real examples. Be conversational but insightful.
When users share ideas, ask probing questions like Lenny would.""",
            },
            "vc": {
                "name": "🦈 Seed VC / Angel Investor",
                "model": "perplexity/sonar-pro",
                "system_prompt": """You are an experienced seed-stage investor and angel investor with access to:
- Current funding market data and trends
- Recent successful fundraising examples
- Real-time valuations and metrics

Focus on:
1. Market timing and TAM analysis
2. Founder-market fit assessment
3. Early traction metrics that matter
4. Unit economics and burn rate
5. Fundraising strategy and deck feedback

Be direct but constructive. Reference recent funding rounds and current market conditions.
Challenge assumptions like a real investor would.""",
            },
        }

    async def get_response(
        self,
        agent_type: str,
        messages: list[dict[str, str]],
        user_message: str,
    ) -> tuple[str, int]:
        """Get AI response for the given agent type."""
        try:
            agent = self.agents[agent_type]

            # Build message history
            formatted_messages = [
                {"role": "system", "content": agent["system_prompt"]},
            ]

            # Add conversation history
            for msg in messages[-10:]:  # Last 10 messages
                formatted_messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["message"],
                    },
                )

            # Add current message
            formatted_messages.append(
                {
                    "role": "user",
                    "content": user_message,
                },
            )

            # Get AI response
            logger.debug(f"Calling OpenRouter with model: {agent['model']}")
            response = await self.client.chat.completions.create(
                model=agent["model"],
                messages=formatted_messages,
                max_tokens=800,
                temperature=0.7,
            )
            logger.debug("Response received successfully")

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0

            return content, tokens

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")

            # Specific error handling for different types of failures
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str:
                return (
                    "Sorry, the AI model is currently unavailable. Try switching agents with /vc or /pm.",
                    0,
                )
            if "401" in error_str or "unauthorized" in error_str:
                return (
                    "API authentication failed. Please check the bot configuration.",
                    0,
                )
            if "429" in error_str or "rate limit" in error_str:
                return (
                    "Too many requests. Please wait a moment and try again.",
                    0,
                )
            if "timeout" in error_str:
                return (
                    "Request timed out. Please try again with a shorter message.",
                    0,
                )
            return (
                "I apologize, but I'm having trouble processing your request. Please try again.",
                0,
            )
