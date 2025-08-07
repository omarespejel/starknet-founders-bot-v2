"""AI agent configurations and OpenRouter integration."""

import logging
import os
import re

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

    def extract_and_format_citations(self, content: str) -> str:
        """Extract citations and convert to inline links."""
        # Pattern to match citations like [1], [2], etc. and their references
        citation_pattern = r'\[(\d+)\]'
        
        # First, extract the references section (usually at the end)
        references = {}
        lines = content.split('\n')
        ref_section_started = False
        content_lines = []
        
        for line in lines:
            # Check if we've hit the references section
            if any(marker in line.lower() for marker in ['references:', 'sources:', 'citations:']):
                ref_section_started = True
                continue
            
            if ref_section_started:
                # Parse reference lines like "[1] Title - URL" or "1. Title - URL"
                ref_match = re.match(r'(?:\[(\d+)\]|(\d+)\.\s*)\s*(.*?)\s*[-–]\s*(https?://\S+)', line)
                if ref_match:
                    ref_num = ref_match.group(1) or ref_match.group(2)
                    ref_title = ref_match.group(3).strip()
                    ref_url = ref_match.group(4).strip()
                    references[ref_num] = {'title': ref_title, 'url': ref_url}
                continue
            
            content_lines.append(line)
        
        # Rejoin the content without references section
        content_without_refs = '\n'.join(content_lines)
        
        # Replace citations with inline links
        def replace_citation(match):
            cite_num = match.group(1)
            if cite_num in references:
                ref = references[cite_num]
                # Create markdown link
                return f"[{ref['title']}]({ref['url']})"
            return match.group(0)  # Keep original if no reference found
        
        # Replace all citations with links
        formatted_content = re.sub(citation_pattern, replace_citation, content_without_refs)
        
        # Log citation processing results
        if references:
            logger.debug(f"Standard citation format detected: {len(references)} references found")
        
        return formatted_content

    def parse_perplexity_citations(self, content: str) -> str:
        """Parse Perplexity's specific citation format."""
        # Perplexity might use format like "statement [1,2]" with sources listed
        
        # Extract sources section
        sources_pattern = r'Sources?:?\s*\n((?:(?:\d+\..*\n?)+))'
        sources_match = re.search(sources_pattern, content, re.MULTILINE)
        
        if sources_match:
            sources_text = sources_match.group(1)
            sources = {}
            
            # Parse each source line
            for line in sources_text.split('\n'):
                match = re.match(r'(\d+)\.\s*(.*?)(?:\s*[-–]\s*)?(https?://\S+)?', line)
                if match:
                    num = match.group(1)
                    title = match.group(2) or "Source"
                    url = match.group(3) or "#"
                    sources[num] = {'title': title.strip(), 'url': url.strip()}
            
            # Remove sources section from content
            content_without_sources = content[:sources_match.start()].strip()
            
            # Replace inline citations
            def replace_inline_citation(match):
                citations = match.group(1).split(',')
                links = []
                for cite in citations:
                    cite = cite.strip()
                    if cite in sources:
                        source = sources[cite]
                        links.append(f"[{source['title']}]({source['url']})")
                
                return ' '.join(links) if links else match.group(0)
            
            # Replace [1,2,3] style citations
            content_with_links = re.sub(r'\[([0-9,\s]+)\]', replace_inline_citation, content_without_sources)
            
            # Log Perplexity citation processing
            logger.debug(f"Perplexity citation format detected: {len(sources)} sources found")
            
            return content_with_links
        
        return content

    def format_response(self, content: str, agent_type: str) -> str:
        """Format AI response with HTML formatting for better reliability."""
        # Debug logging to monitor citation formats
        logger.debug(f"Raw content before citation parsing: {content[:500]}")
        
        # Try Perplexity format first
        content = self.parse_perplexity_citations(content)
        
        # Then try standard citation format
        content = self.extract_and_format_citations(content)
        
        # Convert markdown links to HTML (from citation parsing)
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
        
        # Log if citations were found and processed
        if '<a href=' in content:
            logger.debug("Citations detected and processed in response")
        
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
                    formatted_lines.append(f"<b>{question_count}.</b> {line}")
                else:
                    formatted_lines.append(f"• {line}")
            # Format action items or key points
            elif line.startswith(('-', '*', '•')):
                formatted_lines.append(f"• {line[1:].strip()}")
            # Bold key frameworks and concepts
            elif any(framework in line for framework in ['RICE', 'Jobs-to-be-Done', 'Growth Loop', 'TAM', 'CAC', 'LTV', 'PMF']):
                # Bold the framework names
                for framework in ['RICE', 'Jobs-to-be-Done', 'Growth Loop', 'TAM', 'CAC', 'LTV', 'PMF']:
                    line = line.replace(framework, f"<b>{framework}</b>")
                formatted_lines.append(line)
            # Format section headers (lines that are short and don't end with punctuation)
            elif len(line) < 50 and not line.endswith(('.', '!', '?', ':')):
                formatted_lines.append(f"\n<b>{line}</b>")
            else:
                formatted_lines.append(line)
        
        # Add emoji header based on agent type
        header_emoji = "🚀" if agent_type == "pm" else "💰"
        formatted_content = '\n'.join(formatted_lines)
        
        # Add action item section if not present
        if "next step" not in formatted_content.lower() and "action item" not in formatted_content.lower():
            formatted_content += "\n\n<b>💡 Next Step:</b> Reflect on the above questions and share your thoughts on the most challenging one."
        
        return f"{header_emoji} <b>Response:</b>\n\n{formatted_content}"

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
                max_tokens=500,  # Reduced from 800 to 500 for more concise responses
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
