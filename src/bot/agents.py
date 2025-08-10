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

    def clean_references(self, content: str) -> str:
        """Remove numbered reference citations like [1], [2], [1][3] from content."""
        # Remove single references like [1], [2], [3]
        content = re.sub(r'\[(\d+)\]', '', content)
        
        # Remove multiple consecutive references like [1][2][3]
        content = re.sub(r'(\[\d+\])+', '', content)
        
        # Clean up any double spaces that might result
        content = re.sub(r'\s+', ' ', content)
        
        # Clean up spaces before punctuation
        content = re.sub(r'\s+([.,!?])', r'\1', content)
        
        return content.strip()

    def format_response(self, content: str, agent_type: str) -> str:
        """Format AI response into plain, predictable text suitable for MarkdownV2 escaping.

        We avoid emitting raw HTML or complex Markdown. The caller will escape
        with MarkdownV2 and handle minimal styling.
        """
        logger.debug(f"Raw content before citation parsing: {content[:500]}")

        # Clean numbered references like [1] and inline chains [1][2]
        content = self.clean_references(content)

        # Convert Perplexity/standard citations into inline plain URLs/text
        content = self.parse_perplexity_citations(content)
        content = self.extract_and_format_citations(content)

        # Remove remaining markdown links to just "title - url" plain text
        def md_link_to_plain(match: re.Match[str]) -> str:
            title = match.group(1)
            url = match.group(2)
            return f"{title} - {url}"

        content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", md_link_to_plain, content)

        # Promote inline markdown headings like " ... ### Title" to section breaks
        content = re.sub(r"\s#{2,6}\s+([^\n]+)", r"\n\n\1\n\n", content)

        # Convert separators like '---' or '___' to blank lines
        content = re.sub(r"-{3,}|_{3,}", "\n\n", content)

        # Normalize dashes and convert inline bullets following punctuation/colon into new lines
        content = content.replace("—", "-").replace("–", "-")
        content = re.sub(r"(?:(?<=^)|(?<=[.!?:]))\s*-\s+", "\n- ", content)

        # Remove stray emphasis markers that leak through from the model
        content = content.replace("*", "").replace("_", "").replace("`", "")

        # Build a light, text-first structure: number questions, normalize bullets, handle headings
        raw_lines = content.strip().split("\n")
        lines: list[str] = []
        for raw in raw_lines:
            m = re.match(r"^\s*#{1,6}\s+(.*)$", raw)
            if m:
                title = m.group(1).strip()
                if lines and lines[-1] != "":
                    lines.append("")
                lines.append(title)
                lines.append("")
            else:
                lines.append(raw)

        output_lines: list[str] = []
        question_count = 0
        in_bullet_block = False

        for raw in lines:
            line = raw.strip()
            if not line:
                if output_lines and output_lines[-1] != "":
                    output_lines.append("")
                in_bullet_block = False
                continue

            # Reflow non-list long lines by splitting on sentence boundaries
            if not line.startswith("- ") and len(line) > 160:
                parts = re.split(r"(?<=[.!?])\s+(?=(?:\(|\"|[A-Z0-9]))", line)
                for p in parts:
                    if p:
                        output_lines.append(p.strip())
                output_lines.append("")
                in_bullet_block = False
                continue

            # Remove double prefixes like '1. - '
            line = re.sub(r"^(\d+\.\s*)-\s*", r"\1", line)

            if line.endswith("?"):
                question_count += 1
                # If already numbered like '3. ...', keep as-is to avoid double numbering
                if re.match(r"^\d+\.\s", line):
                    output_lines.append(line)
                else:
                    prefix = f"{question_count}. " if question_count <= 7 else "- "
                    output_lines.append(f"{prefix}{line}")
                in_bullet_block = False
            elif line.startswith(("- ", "* ", "• ")):
                if not in_bullet_block and output_lines and output_lines[-1] != "":
                    output_lines.append("")
                output_lines.append(f"- {line.lstrip('-*• ').strip()}")
                in_bullet_block = True
            else:
                output_lines.append(line)
                in_bullet_block = False

        header_emoji = "🚀" if agent_type == "pm" else "💰"
        # Ensure extra spacing after complete sentences for readability
        spaced_lines: list[str] = []
        for idx, line in enumerate(output_lines):
            spaced_lines.append(line)
            if (
                line
                and not line.startswith("- ")
                and not re.match(r"^\d+\.\s", line)
                and line[-1] in ".?!"
            ):
                # If next line exists and is non-empty, insert a blank line
                nxt = output_lines[idx + 1] if idx + 1 < len(output_lines) else ""
                if nxt and nxt.strip() != "":
                    spaced_lines.append("")

        # Collapse excessive blank lines to at most two and trim
        text = "\n".join(spaced_lines)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        if "next step" not in text.lower() and "action item" not in text.lower():
            text += "\n\nNext Step: Reflect on the above questions and share your thoughts on the most challenging one."

        return f"{header_emoji} Response\n\n{text}"

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
