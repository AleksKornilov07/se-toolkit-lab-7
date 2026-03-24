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

## Deploy

### Prerequisites

- Docker and Docker Compose installed on VM
- Backend service running (`se-toolkit-lab-7-backend-1`)
- Qwen Code API proxy accessible

### Environment Variables

Create `.env.docker.secret` in the project root with:

```env
# Telegram Bot
BOT_TOKEN=<your-bot-token>

# LMS API (internal Docker network)
LMS_API_KEY=<your-lms-api-key>

# LLM API (use host.docker.internal for Docker access)
LLM_API_KEY=<your-llm-api-key>
LLM_API_BASE_URL=http://host.docker.internal:42005/v1
LLM_API_MODEL=coder-model
```

> **Note:** `LLM_API_BASE_URL` uses `host.docker.internal` instead of `localhost` because the bot runs inside a Docker container and needs to reach the Qwen proxy on the host machine.

### Deploy Commands

```bash
cd ~/se-toolkit-lab-7

# Stop the background bot process (if running)
pkill -f "bot.py" 2>/dev/null

# Build and start all services
docker compose --env-file .env.docker.secret up --build -d

# Check status
docker compose --env-file .env.docker.secret ps

# Check bot logs
docker compose --env-file .env.docker.secret logs bot --tail 50
```

### Verify Deployment

1. **Check container is running:**
   ```bash
   docker compose ps bot
   ```

2. **Check logs for errors:**
   ```bash
   docker compose logs bot --tail 20
   ```
   Look for "Application started" and no Python tracebacks.

3. **Test in Telegram:**
   - `/start` — welcome message
   - `/health` — backend status
   - "what labs are available?" — natural language query
   - "which lab has the lowest pass rate?" — multi-step reasoning

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container restarting | Check logs: `docker compose logs bot` |
| LLM queries fail | Use `host.docker.internal` in `LLM_API_BASE_URL` |
| Backend connection failed | Use `http://backend:8000` not `localhost:42002` |
| BOT_TOKEN error | Ensure env vars are in `.env.docker.secret` |
