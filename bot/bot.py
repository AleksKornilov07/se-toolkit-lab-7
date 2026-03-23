#!/usr/bin/env python3
"""
Telegram Bot for Learning Management System.

Usage:
    uv run bot.py                  # Run Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
"""

import asyncio
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
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


async def run_test_mode(command: str) -> None:
    """
    Run bot in test mode - call handlers directly without Telegram.

    Args:
        command: Command string like "/start" or "/scores lab-01"
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    response: Optional[str] = None

    # Route to appropriate handler
    if cmd == "/start":
        response = await handle_start()
    elif cmd == "/help":
        response = await handle_help()
    elif cmd == "/health":
        # Check backend health
        is_healthy = await lms_client.health_check()
        if is_healthy:
            response = "✅ Bot is running. Backend connection: OK"
        else:
            response = "⚠️ Bot is running. Backend connection: FAILED"
    elif cmd == "/labs":
        response = await handle_labs()
    elif cmd == "/scores":
        response = await handle_scores(arg)
    else:
        # Try LLM intent classification for natural language
        intent = await llm_client.classify_intent(command)
        if intent != "unknown":
            # Re-route based on classified intent
            if intent == "start":
                response = await handle_start()
            elif intent == "help":
                response = await handle_help()
            elif intent == "health":
                is_healthy = await lms_client.health_check()
                response = "✅ Backend OK" if is_healthy else "⚠️ Backend FAILED"
            elif intent == "labs":
                response = await handle_labs()
            elif intent == "scores":
                # Extract lab name from message using LLM
                response = await llm_client.answer_question(
                    command,
                    "Available labs: lab-01, lab-02, lab-03, lab-04"
                )
        else:
            # General question - use LLM
            response = await llm_client.answer_question(command)

    # Print response to stdout
    print(response)


# -----------------------------------------------------------------------------
# Telegram Bot Mode
# -----------------------------------------------------------------------------


async def setup_bot() -> tuple[Bot, Dispatcher]:
    """Initialize bot and dispatcher."""
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    return bot, dp


def register_handlers(dp: Dispatcher) -> None:
    """Register all command handlers."""

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        response = await handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        response = await handle_help()
        await message.answer(response)

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
        """Handle natural language messages with LLM intent routing."""
        text = message.text or ""

        # Classify intent
        intent = await llm_client.classify_intent(text)

        if intent == "start":
            response = await handle_start()
        elif intent == "help":
            response = await handle_help()
        elif intent == "health":
            is_healthy = await lms_client.health_check()
            response = "✅ Backend OK" if is_healthy else "⚠️ Backend FAILED"
        elif intent == "labs":
            response = await handle_labs()
        elif intent == "scores":
            # Use LLM to extract lab name and generate response
            context = "Available labs: lab-01, lab-02, lab-03, lab-04"
            response = await llm_client.answer_question(text, context)
        else:
            # General question
            response = await llm_client.answer_question(text)

        await message.answer(response)


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
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            sys.exit(1)

        command = sys.argv[2]
        await run_test_mode(command)
        return

    # Run Telegram bot
    await run_telegram_mode()


if __name__ == "__main__":
    asyncio.run(main())
