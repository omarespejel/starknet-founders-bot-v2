"""Middleware for error handling and logging."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user."""
    logger.error(f"Exception while handling an update: {context.error}")

    # Notify user
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😔 Sorry, something went wrong. Please try again or use /help."
        )
