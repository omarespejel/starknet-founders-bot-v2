"""Main application entry point."""

import os

def main():
    """Main entry point that chooses the right bot mode."""
    # Check if we're in production (Render sets PORT environment variable)
    if os.getenv("PORT"):
        # Production: Use webhook mode
        from src.bot.webhook_main import main as webhook_main
        webhook_main()
    else:
        # Development: Use polling mode
        from src.bot.main import main as polling_main
        polling_main()


if __name__ == "__main__":
    main()
