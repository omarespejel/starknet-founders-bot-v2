# Starknet Founders Bot v2

AI-powered Telegram bot for Starknet founders with two expert advisor personalities.

## Features

- **Product Manager Mode**: Based on Lenny Rachitsky's frameworks
- **VC/Angel Investor Mode**: Current market insights and fundraising advice
- **Real-time Data**: Powered by Perplexity with internet access
- **Conversation Memory**: Persistent chat history with Supabase
- **Usage Analytics**: Track your conversations and statistics

## 🛠️ Tech Stack

- Python 3.11+ with UV package manager
- Telegram Bot API (python-telegram-bot)
- OpenRouter API (Perplexity models)
- Supabase (PostgreSQL database)
- Async/await architecture

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies: `uv sync`
4. Run migrations in Supabase
5. Start the bot: `uv run python -m bot.main`

## Usage

1. Start chat: [@starknet_advisor_bot](https://t.me/starknet_advisor_bot)
2. Choose your advisor (PM or VC)
3. Ask questions about your startup!

## 🔑 Environment Variables

See `.env.example` for required variables.

## 📄 License

MIT

---

Built with ❤️ for the Starknet ecosystem