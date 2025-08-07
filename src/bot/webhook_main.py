"""Webhook-based bot application for production deployment."""

import logging
import os
import sys
from typing import NoReturn

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from fastapi import FastAPI, Request
from fastapi.responses import Response
import uvicorn

from .config import TELEGRAM_BOT_TOKEN
from .handlers import BotHandlers
from .middleware import error_handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# FastAPI app for webhook
app = FastAPI(title="Telegram Bot Webhook")

# Global application variable
application: Application = None


def create_application() -> Application:
    """Create and configure the telegram application."""
    # Create application
    app_instance = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Initialize handlers
    handlers = BotHandlers()

    # Register command handlers
    app_instance.add_handler(CommandHandler("start", handlers.start))
    app_instance.add_handler(CommandHandler("pm", handlers.switch_to_pm))
    app_instance.add_handler(CommandHandler("vc", handlers.switch_to_vc))
    app_instance.add_handler(CommandHandler("reset", handlers.reset))
    app_instance.add_handler(CommandHandler("stats", handlers.stats))
    app_instance.add_handler(CommandHandler("help", handlers.help_command))

    # Register callback query handler for inline keyboards
    app_instance.add_handler(
        CallbackQueryHandler(
            handlers.handle_agent_selection,
            pattern="^select_",
        )
    )

    # Register message handler for regular text
    app_instance.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handlers.handle_message,
        )
    )

    # Add error handler
    app_instance.add_error_handler(error_handler)

    return app_instance


@app.on_event("startup")
async def startup():
    """Initialize the telegram application on startup."""
    global application
    application = create_application()
    await application.initialize()
    await application.start()
    
    # Set webhook
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"Webhook set to {webhook_url}/webhook")
    else:
        logger.warning("WEBHOOK_URL not set, webhook not configured")


@app.on_event("shutdown")
async def shutdown():
    """Clean up on shutdown."""
    if application:
        await application.stop()
        await application.shutdown()


@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook updates."""
    try:
        # Get the update data
        data = await request.json()
        update = Update.de_json(data, application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return Response(status_code=500)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "bot": "running"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


def main() -> NoReturn:
    """Start the webhook server."""
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting webhook server on port {port}")
    
    uvicorn.run(
        "src.bot.webhook_main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
