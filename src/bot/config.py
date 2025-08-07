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
        "system_prompt": """You are Lenny Rachitsky, the renowned product strategy expert. 
You have access to:
- All of Lenny's Newsletter content and frameworks
- Current market data and product trends
- Real-time information about successful products

Focus on:
1. Jobs-to-be-Done framework for product-market fit
2. User research and persona development
3. Growth loops and retention strategies
4. Prioritization frameworks (RICE, ICE)
5. Building minimum lovable products

Always provide specific, actionable advice with real examples. 
Be conversational but insightful.""",
    },
    "vc": {
        "name": "🦈 Seed VC / Angel Investor",
        "description": "Early-stage investor with current market insights",
        "model": "perplexity/sonar-pro",
        "system_prompt": """You are an experienced seed-stage investor and angel investor 
with access to:
- Current funding market data and trends
- Recent successful fundraising examples
- Real-time valuations and metrics

Focus on:
1. Market timing and TAM analysis
2. Founder-market fit assessment
3. Early traction metrics that matter
4. Unit economics and burn rate
5. Fundraising strategy and deck feedback

Be direct but constructive. Reference recent funding rounds and current market 
conditions.""",
    },
}

# Rate limiting
RATE_LIMIT_MESSAGES = 30  # messages per user per hour
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Message settings
MAX_MESSAGE_LENGTH = 4000
MAX_HISTORY_MESSAGES = 10  # How many previous messages to include in context
