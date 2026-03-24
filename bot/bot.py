#!/usr/bin/env python3
"""
Telegram Bot for Learning Management System.

Usage:
    uv run bot.py                  # Run Telegram bot
    uv run bot.py --test "hello"   # Test mode (no Telegram connection)
"""

import asyncio
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from services import lms_client, llm_client


# -----------------------------------------------------------------------------
# Test Mode
# -----------------------------------------------------------------------------


async def run_test_mode(message: str) -> None:
    """
    Run bot in test mode - use LLM routing directly.

    Args:
        message: Message string like "/start" or "which lab has the lowest pass rate"
    """
    text = message.strip()

    # Handle slash commands directly
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        response: Optional[str] = None

        if cmd == "/start":
            response = await handle_start()
        elif cmd == "/help":
            response = await handle_help()
        elif cmd == "/health":
            is_healthy = await lms_client.health_check()
            response = "✅ Bot is running. Backend connection: OK" if is_healthy else "⚠️ Bot is running. Backend connection: FAILED"
        elif cmd == "/labs":
            response = await handle_labs()
        elif cmd == "/scores":
            response = await handle_scores(arg)
        else:
            response = f"Unknown command: {cmd}"

        print(response)
        return

    # Natural language - use LLM routing
    response = await llm_client.route(text, lms_client)
    print(response)


# -----------------------------------------------------------------------------
# Telegram Bot Mode
# -----------------------------------------------------------------------------


async def setup_bot() -> tuple[Bot, Dispatcher]:
    """Initialize bot and dispatcher."""
    bot = Bot(token=settings.bot_token, parse_mode="HTML")
    dp = Dispatcher()
    return bot, dp


def register_handlers(dp: Dispatcher) -> None:
    """Register all command handlers."""

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        response = await handle_start()
        await message.answer(response, reply_markup=await get_main_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        response = await handle_help()
        await message.answer(response, reply_markup=await get_main_keyboard())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message) -> None:
        is_healthy = await lms_client.health_check()
        if is_healthy:
            response = "✅ Bot is running. Backend connection: OK"
        else:
            response = "⚠️ Bot is running. Backend connection: FAILED"
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message) -> None:
        response = await handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message) -> None:
        # Get lab argument from command
        lab = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        response = await handle_scores(lab)
        await message.answer(response)

    @dp.message()
    async def handle_message(message: types.Message) -> None:
        """Handle natural language messages with LLM tool routing."""
        text = message.text or ""

        # Use LLM routing with tool calling
        response = await llm_client.route(text, lms_client)
        await message.answer(response)


async def get_main_keyboard() -> types.InlineKeyboardMarkup:
    """Create inline keyboard with common actions."""
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📚 Labs", callback_data="labs"),
                types.InlineKeyboardButton(text="📊 Scores", callback_data="scores"),
            ],
            [
                types.InlineKeyboardButton(text="💚 Health", callback_data="health"),
                types.InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
        ]
    )
    return keyboard


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode."""
    if not settings.bot_token:
        print("Error: BOT_TOKEN is not set. Please configure .env.bot.secret")
        sys.exit(1)

    bot, dp = await setup_bot()
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await lms_client.close()
        await llm_client.close()


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------


async def main() -> None:
    """Main entry point."""
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <message>")
            print("Example: uv run bot.py --test 'what labs are available'")
            sys.exit(1)

        message = sys.argv[2]
        await run_test_mode(message)
        return

    # Run Telegram bot
    await run_telegram_mode()


if __name__ == "__main__":
    asyncio.run(main())
