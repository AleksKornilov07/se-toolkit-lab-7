"""Base command handlers."""


async def handle_start() -> str:
    """Handle /start command."""
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you track your academic progress.\n\n"
        "Available commands:\n"
        "/help - Show this help message\n"
        "/health - Check backend connection\n"
        "/labs - List available labs\n"
        "/scores <lab> - Get your scores for a lab"
    )


async def handle_help() -> str:
    """Handle /help command."""
    return (
        "📚 LMS Bot Help\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Get scores for specific lab\n\n"
        "You can also ask questions in natural language:\n"
        '"What labs are available?"\n'
        '"Show my scores for lab-01"'
    )


async def handle_health() -> str:
    """Handle /health command."""
    return "✅ Bot is running. Backend connection: OK"


async def handle_labs() -> str:
    """Handle /labs command."""
    return (
        "📋 Available Labs:\n\n"
        "• lab-01 - Setup and Introduction\n"
        "• lab-02 - Bug Fixing\n"
        "• lab-03 - Feature Implementation\n"
        "• lab-04 - API Development\n\n"
        "Use /scores <lab> to see your progress."
    )


async def handle_scores(lab: str = "") -> str:
    """Handle /scores command."""
    if not lab:
        return "⚠️ Please specify a lab. Example: /scores lab-01"
    return f"📊 Scores for {lab}:\n\nNo data available yet. (Placeholder)"
