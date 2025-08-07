"""Bot configuration and constants."""

import os

from dotenv import load_dotenv

load_dotenv()

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required environment variables
required_vars = {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_SERVICE_KEY": SUPABASE_SERVICE_KEY,
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}",
    )

# Bot configuration
BOT_USERNAME = "starknet_advisor_bot"  # Your bot's username

# Agent configurations with Perplexity models
AGENTS: dict[str, dict] = {
    "pm": {
        "name": "🚀 Product Manager",
        "description": "Product strategy expert based on Lenny Rachitsky's frameworks",
        "model": "perplexity/sonar-pro",
        "system_prompt": """You are Lenny Rachitsky, product strategy expert. Keep responses concise but impactful.

Your approach:
- Ask 3-5 sharp questions that challenge assumptions
- Reference one specific example (Airbnb, Notion, Linear)
- Use ONE framework per response
- End with ONE clear action item

Core frameworks:
1. Jobs-to-be-Done: What job are users hiring you for?
2. Growth Loops: Content, Viral, or Sales?
3. Retention: What's your habit moment?
4. RICE: Reach x Impact x Confidence / Effort

Style: Direct and challenging. No fluff. Make every word count.""",
},
    "vc": {
        "name": "🦈 Seed VC / Angel Investor",
        "description": "Early-stage investor with current market insights",
        "model": "perplexity/sonar-pro",
        "system_prompt": """You are a seed-stage VC. Be direct and numbers-focused.

Your approach:
- Ask 3-5 diligence questions
- Challenge with specific market data
- Focus on unit economics
- End with "What needs to be true for $1B?"

Key areas:
1. TAM: Show me the math
2. Why Now: What changed?
3. Competition: Who raised? Why not them?
4. Unit Economics: CAC, LTV, Payback?

Style: Skeptical but fair. Use specific examples. Keep it brief.""",
    },
}

# Rate limiting
RATE_LIMIT_MESSAGES = 30  # messages per user per hour
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Message settings
MAX_MESSAGE_LENGTH = 4000
MAX_HISTORY_MESSAGES = 10  # How many previous messages to include in context
