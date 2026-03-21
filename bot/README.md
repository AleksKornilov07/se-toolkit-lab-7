# LMS Telegram Bot

Telegram bot for Learning Management System analytics.

## Usage

```bash
# Run in Telegram mode
uv run bot.py

# Run in test mode
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-01"
```

## Configuration

Copy `.env.bot.example` to `.env.bot.secret` and fill in your values.
