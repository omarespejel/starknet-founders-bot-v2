"""Test Telegram bot connection."""

import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


async def test_bot() -> None:
    """Test bot token and get bot info."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ No TELEGRAM_BOT_TOKEN found in .env")
        return

    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()

        print("✅ Bot connected successfully!")
        print(f"🤖 Bot name: {bot_info.first_name}")
        print(f"📱 Bot username: @{bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print(f"💬 Can join groups: {bot_info.can_join_groups}")
        print(f"📖 Can read all group messages: {bot_info.can_read_all_group_messages}")

    except Exception as e:
        print(f"❌ Error connecting to bot: {e}")


if __name__ == "__main__":
    asyncio.run(test_bot())
