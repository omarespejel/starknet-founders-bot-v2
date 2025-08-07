"""Telegram bot command handlers."""

import io
import logging
import re
from datetime import UTC, datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from .agents import AIAgent
from .config import AGENTS
from .database import Database
from .exporters import ConversationExporter
from .utils import rate_limiter

logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles all bot commands and messages."""

    def __init__(self) -> None:
        self.db = Database()
        self.ai = AIAgent()

    async def log_analytics(self, user_id: str, action: str, metadata: dict = None):
        """Log analytics events."""
        try:
            self.db.client.table("bot_analytics").insert(
                {
                    "user_id": user_id,
                    "action": action,
                    "metadata": metadata or {},
                    "created_at": datetime.now(UTC).isoformat(),
                }
            ).execute()
        except Exception:
            pass  # Don't let analytics errors break the bot

    async def get_conversation_summary(self, user_id: str, agent_type: str) -> str:
        """Generate a summary of key points from conversation history."""
        try:
            # Get last 20 messages
            history = await self.db.get_conversation_history(
                user_id=user_id,
                agent_type=agent_type,
                limit=20
            )
            
            if len(history) < 4:  # Not enough history
                return ""
            
            # Extract key topics discussed
            user_messages = [msg['message'] for msg in history if msg['role'] == 'user']
            
            # Simple keyword extraction for continuity
            key_topics = []
            keywords = ['product', 'users', 'market', 'growth', 'revenue', 'competition', 'funding', 'team']
            
            for keyword in keywords:
                if any(keyword in msg.lower() for msg in user_messages):
                    key_topics.append(keyword)
            
            if not key_topics:
                return ""
                
            return f"Building on our discussion about {', '.join(key_topics[:3])}... "
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return ""

    async def generate_ai_summary(self, user_id: str, agent_type: str) -> str:
        """Generate AI-powered summary of last 4 exchanges."""
        try:
            # Get last 8 messages (4 user + 4 assistant)
            history = await self.db.get_conversation_history(
                user_id=user_id,
                agent_type=agent_type,
                limit=8
            )
            
            if not history:
                return "No recent conversation to summarize."
            
            # Format conversation for summary
            conversation_text = ""
            for msg in history:
                role = "User" if msg['role'] == 'user' else "Advisor"
                conversation_text += f"{role}: {msg['message'][:200]}...\n"
            
            # Summary prompt
            summary_prompt = """Summarize this startup advisory session in 3 bullet points:
            - Key insight discovered
            - Main challenge identified  
            - Next action to take
            Keep each point under 15 words."""
            
            messages = [
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": f"Session: {conversation_text}"}
            ]
            
            response = await self.ai.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for summaries
                messages=messages,
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return "Unable to generate summary at this time."

    async def start(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user

        # Create agent selection keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    AGENTS["pm"]["name"],
                    callback_data="select_pm",
                )
            ],
            [
                InlineKeyboardButton(
                    AGENTS["vc"]["name"],
                    callback_data="select_vc",
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = f"""
Welcome to Starknet Startup Advisor Bot (Beta).

Hello {user.first_name}. I provide AI-powered guidance through two specialized advisors:

**Product Manager**
Strategic product development guidance
- Challenges your assumptions about users
- Questions your product-market fit approach  
- Probes your growth and retention strategies
- Helps prioritize features that matter

**VC/Angel Investor**
Early-stage investment perspective
- Questions market size and opportunity
- Challenges your competitive positioning
- Probes unit economics and metrics
- Tests your fundraising readiness

Choose your advisor to begin:
"""

        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )

        # Update user session
        await self.db.update_user_session(
            user_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            agent_type="pm",  # Default
        )

        # Log analytics
        await self.log_analytics(
            user_id=str(user.id),
            action="bot_started",
            metadata={"username": user.username, "first_name": user.first_name},
        )

    async def handle_agent_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle agent selection from inline keyboard."""
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        agent_type = query.data.replace("select_", "")

        # Update user session
        await self.db.update_user_session(
            user_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            agent_type=agent_type,
        )

        # Store in context for quick access
        context.user_data["agent_type"] = agent_type

        # Log analytics
        await self.log_analytics(
            user_id=str(user.id),
            action="agent_selected",
            metadata={
                "agent_type": agent_type,
                "agent_name": AGENTS[agent_type]["name"],
            },
        )

        agent_name = AGENTS[agent_type]["name"]
        agent_desc = AGENTS[agent_type]["description"]

        start_prompts = {
            "pm": [
                "What problem are you solving?",
                "Who is your target user?",
                "What's your current product stage?",
                "What are you struggling with?"
            ],
            "vc": [
                "What's your business model?",
                "How big is your market?",
                "What's your competitive advantage?",
                "What metrics are you tracking?"
            ]
        }

        prompts = "\n- ".join(start_prompts[agent_type])

        await query.edit_message_text(
            f"""
{agent_name} selected.

I'll challenge your thinking and ask probing questions to help refine your strategy.

Start by sharing:
- {prompts}

Or tell me about your startup.

Switch advisors anytime with /pm or /vc
""",
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle regular text messages."""
        user = update.effective_user
        message = update.message.text

        # Check rate limit
        allowed, error_msg = rate_limiter.is_allowed(user.id)
        if not allowed:
            await update.message.reply_text(
                f"⚠️ {error_msg}\n\nThis limit helps ensure quality service for all users.",
                parse_mode=ParseMode.MARKDOWN,
            )
            
            # Log rate limiting analytics
            await self.log_analytics(
                user_id=str(user.id),
                action="rate_limited",
                metadata={"error_msg": error_msg}
            )
            return

        # Get or set agent type
        agent_type = context.user_data.get("agent_type", "pm")

        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        try:
            # Save user message
            await self.db.save_message(
                user_id=str(user.id),
                username=user.username,
                first_name=user.first_name,
                agent_type=agent_type,
                role="user",
                message=message,
            )

            # Get conversation history
            history = await self.db.get_conversation_history(
                user_id=str(user.id),
                agent_type=agent_type,
                limit=10,
            )

            # Add conversation continuity for returning users
            continuity_prefix = ""
            if len(history) > 4:  # Has meaningful history
                continuity_prefix = await self.get_conversation_summary(str(user.id), agent_type)

            # Get AI response with continuity context
            if continuity_prefix:
                # Prepend continuity to user message for context
                contextualized_message = f"[Continue from previous discussion: {continuity_prefix}]\n\nUser says: {message}"
            else:
                contextualized_message = message

            # Get AI response
            ai_response, tokens = await self.ai.get_response(
                agent_type=agent_type,
                messages=history,
                user_message=contextualized_message,
            )

            # Save AI response
            await self.db.save_message(
                user_id=str(user.id),
                username=user.username,
                first_name=user.first_name,
                agent_type=agent_type,
                role="assistant",
                message=ai_response,
                tokens_used=tokens,
            )

            # Send response
            try:
                await update.message.reply_text(
                    ai_response,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                # If HTML fails, try without formatting
                logger.warning(f"HTML parsing failed: {e}")
                # Strip HTML tags for plain text fallback
                plain_text = re.sub(r'<[^>]+>', '', ai_response)
                await update.message.reply_text(
                    plain_text,
                    parse_mode=None,
                    disable_web_page_preview=True,
                )

            # Log analytics
            await self.log_analytics(
                user_id=str(user.id),
                action="message_processed",
                metadata={
                    "agent_type": agent_type,
                    "message_length": len(message),
                    "response_length": len(ai_response),
                    "tokens_used": tokens,
                },
            )

            # Check if we should generate a summary (every 4 user messages)
            message_count = await self.db.get_message_count(str(user.id), agent_type)
            
            if message_count > 0 and message_count % 4 == 0:
                # Generate and send summary
                summary = await self.generate_ai_summary(str(user.id), agent_type)
                
                summary_message = f"""
📊 <b>Progress Summary (Last 4 exchanges):</b>

{summary}

<i>Keep going! What's your next question?</i>
"""
                await update.message.reply_text(
                    summary_message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                
                # Save summary to database
                await self.db.save_conversation_summary(
                    user_id=str(user.id),
                    agent_type=agent_type,
                    summary=summary
                )

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error. Please try again.",
            )

            # Log error analytics
            await self.log_analytics(
                user_id=str(user.id),
                action="message_error",
                metadata={"agent_type": agent_type, "error": str(e)[:100]},
            )

    async def switch_to_pm(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /pm command."""
        await self._switch_agent(update, context, "pm")

    async def switch_to_vc(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /vc command."""
        await self._switch_agent(update, context, "vc")

    async def _switch_agent(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        agent_type: str,
    ) -> None:
        """Switch to a different agent."""
        user = update.effective_user

        # Update session
        await self.db.update_user_session(
            user_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            agent_type=agent_type,
        )

        context.user_data["agent_type"] = agent_type

        # Log analytics
        await self.log_analytics(
            user_id=str(user.id),
            action="agent_switched",
            metadata={
                "new_agent_type": agent_type,
                "agent_name": AGENTS[agent_type]["name"],
            },
        )

        agent_name = AGENTS[agent_type]["name"]
        await update.message.reply_text(
            f"✅ Switched to **{agent_name}**\n\nHow can I help you?",
            parse_mode=ParseMode.MARKDOWN,
        )

    async def reset(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /reset command."""
        user = update.effective_user
        agent_type = context.user_data.get("agent_type", "pm")

        # Clear conversation history for current agent
        await self.db.clear_conversation(user_id=str(user.id), agent_type=agent_type)

        agent_name = AGENTS[agent_type]["name"]
        await update.message.reply_text(
            f"🔄 **Conversation Reset!**\n\nYour conversation history with {agent_name} has been cleared.\n\nLet's start fresh! What would you like to discuss?",
            parse_mode=ParseMode.MARKDOWN,
        )

        # Log analytics
        await self.log_analytics(
            user_id=str(user.id),
            action="conversation_reset",
            metadata={"agent_type": agent_type, "agent_name": agent_name},
        )

    async def stats(
        self,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /stats command."""
        user = update.effective_user

        # Get user stats
        stats = await self.db.get_user_stats(str(user.id))

        # Format dates
        if stats["first_message_date"]:
            first_date = datetime.fromisoformat(
                stats["first_message_date"].replace("Z", "+00:00")
            )
            # Ensure both datetimes are timezone-aware for proper comparison
            days_active = (datetime.now(UTC) - first_date).days
            member_since = first_date.strftime("%B %d, %Y")
        else:
            days_active = 0
            member_since = "Today"

        # Determine favorite advisor
        if stats['pm_messages'] > stats['vc_messages']:
            favorite = "🚀 Product Manager"
        elif stats['vc_messages'] > stats['pm_messages']:
            favorite = "🦈 VC/Angel"
        else:
            favorite = "Both equally!"
        
        stats_message = f"""
📊 <b>Your Statistics</b>

👤 <b>User:</b> {user.first_name or 'Founder'}
📅 <b>Member Since:</b> {member_since}
⏱️ <b>Days Active:</b> {days_active}

💬 <b>Total Messages:</b> {stats['total_messages']}
├─ 🚀 PM: {stats['pm_messages']}
└─ 🦈 VC: {stats['vc_messages']}

⭐ <b>Favorite:</b> {favorite}

<i>Beta version • Feedback: @espejelomar</i>
"""

        await update.message.reply_text(
            stats_message,
            parse_mode=ParseMode.HTML
        )

        # Log analytics
        await self.log_analytics(
            user_id=str(user.id),
            action="stats_viewed",
            metadata={
                "total_messages": stats["total_messages"],
                "pm_messages": stats["pm_messages"],
                "vc_messages": stats["vc_messages"],
                "days_active": days_active,
            },
        )

    async def help_command(
        self,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /help command."""
        help_text = """
**How to use this bot:**

**Commands:**
- /start - Choose your advisor
- /pm - Switch to Product Manager
- /vc - Switch to VC/Angel Investor  
- /reset - Clear conversation history
- /stats - View your usage stats
- /help - Show this help message

**Tips:**
- Be specific about your startup/product
- Ask follow-up questions
- Share your challenges openly
- The AI has internet access for current data

**Beta Version**
This bot is in beta. Your feedback helps improve it.
Report bugs or suggestions to @espejelomar

Current advisor: Check bot responses to see which mode is active.
"""

        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
        )

    async def export_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /export command."""
        user = update.effective_user
        agent_type = context.user_data.get("agent_type", "pm")
        
        # Show export options
        keyboard = [
            [
                InlineKeyboardButton("📝 Markdown", callback_data="export_markdown"),
                InlineKeyboardButton("📄 PDF", callback_data="export_pdf")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Choose export format:",
            reply_markup=reply_markup
        )

    async def handle_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle export callback."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        agent_type = context.user_data.get("agent_type", "pm")
        export_type = query.data.replace("export_", "")
        
        # Get conversation history
        messages = await self.db.get_conversation_history(
            user_id=str(user.id),
            agent_type=agent_type,
            limit=50  # Export last 50 messages
        )
        
        if not messages:
            await query.edit_message_text("No conversation history to export.")
            return
        
        user_info = {
            "first_name": user.first_name,
            "username": user.username
        }
        
        exporter = ConversationExporter()
        
        try:
            if export_type == "markdown":
                # Generate markdown
                md_content = await exporter.export_to_markdown(messages, user_info)
                
                # Send as document
                bio = io.BytesIO(md_content.encode())
                bio.name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=bio,
                    caption="📝 Your conversation in Markdown format"
                )
            
            elif export_type == "pdf":
                # Generate PDF
                pdf_bytes = await exporter.export_to_pdf(messages, user_info)
                
                # Send as document
                bio = io.BytesIO(pdf_bytes)
                bio.name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=bio,
                    caption="📄 Your conversation in PDF format"
                )
            
            await query.edit_message_text("✅ Export complete!")
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            await query.edit_message_text("❌ Export failed. Please try again later.")
