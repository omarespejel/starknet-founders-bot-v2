"""AI agent configurations and OpenRouter integration."""

import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .config import AGENTS

load_dotenv()

logger = logging.getLogger(__name__)


class AIAgent:
    """Manages AI agent interactions with OpenRouter."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # Use agent configurations from config.py
        self.agents = AGENTS

    def format_response(self, content: str, agent_type: str) -> str:
        """Format AI response with proper markdown."""
        # Split content into sections
        lines = content.strip().split('\n')
        formatted_lines = []
        question_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
                continue
                
            # Format questions (lines ending with ?)
            if line.endswith('?'):
                question_count += 1
                if question_count <= 7:  # First 5-7 questions get numbered
                    formatted_lines.append(f"**{question_count}.** {line}")
                else:
                    formatted_lines.append(f"• {line}")
            # Format action items or key points
            elif line.startswith(('-', '*', '•')):
                formatted_lines.append(f"• {line[1:].strip()}")
            # Bold key frameworks and concepts
            elif any(framework in line for framework in ['RICE', 'Jobs-to-be-Done', 'Growth Loop', 'TAM', 'CAC', 'LTV', 'PMF']):
                # Bold the framework names
                for framework in ['RICE', 'Jobs-to-be-Done', 'Growth Loop', 'TAM', 'CAC', 'LTV', 'PMF']:
                    line = line.replace(framework, f"**{framework}**")
                formatted_lines.append(line)
            # Format section headers (lines that are short and don't end with punctuation)
            elif len(line) < 50 and not line.endswith(('.', '!', '?', ':')):
                formatted_lines.append(f"\n**{line}**")
            else:
                formatted_lines.append(line)
        
        # Add emoji header based on agent type
        header_emoji = "🚀" if agent_type == "pm" else "💰"
        formatted_content = '\n'.join(formatted_lines)
        
        # Add action item section if not present
        if "next step" not in formatted_content.lower() and "action item" not in formatted_content.lower():
            formatted_content += "\n\n**💡 Next Step:** Reflect on the above questions and share your thoughts on the most challenging one."
        
        return f"{header_emoji} **Response:**\n\n{formatted_content}"

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

            # Format the response with markdown
            formatted_content = self.format_response(content, agent_type)

            return formatted_content, tokens

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
