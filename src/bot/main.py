"""Main bot application."""

import logging
import signal
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from .config import TELEGRAM_BOT_TOKEN
from .handlers import BotHandlers
from .middleware import error_handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Initialize handlers
    handlers = BotHandlers()

    # Register command handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("pm", handlers.switch_to_pm))
    application.add_handler(CommandHandler("vc", handlers.switch_to_vc))
    application.add_handler(CommandHandler("reset", handlers.reset))
    application.add_handler(CommandHandler("stats", handlers.stats))
    application.add_handler(CommandHandler("help", handlers.help_command))

    # Register callback query handler for inline keyboards
    application.add_handler(
        CallbackQueryHandler(
            handlers.handle_agent_selection,
            pattern="^select_",
        )
    )

    # Register message handler for regular text
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handlers.handle_message,
        )
    )

    # Add error handler
    application.add_error_handler(error_handler)

    # Add graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping bot...")
        application.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
