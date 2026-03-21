# Telegram Bot Development Plan

## Overview

This document outlines the development plan for the Learning Management System (LMS) Telegram bot. The bot provides students with quick access to their academic progress, lab submissions, scores, and analytics through a conversational interface.

## Architecture

The bot follows a layered architecture with clear separation of concerns:

1. **Entry Point (`bot.py`)**: Handles Telegram webhook/polling and CLI test mode. Routes incoming messages to appropriate handlers.

2. **Handlers (`handlers/`)**: Command logic isolated from Telegram-specific code. Each handler is a pure function that takes input data and returns a response string. This design enables offline testing via `--test` mode.

3. **Services (`services/`)**: External API clients (LMS API, LLM API) encapsulated in service classes. Handlers depend on services, not directly on HTTP libraries.

4. **Configuration (`config.py`)**: Centralized environment variable loading with validation.

## Development Tasks

### Task 1: Project Scaffold (Current)
- Create directory structure with `handlers/`, `services/`
- Implement `--test` mode for offline verification
- Set up `pyproject.toml` with dependencies (aiogram, httpx, pydantic-settings)
- Document architecture in PLAN.md

### Task 2: Core Commands
- `/start` - Welcome message with user registration
- `/help` - List of available commands
- `/health` - Backend connectivity check
- `/labs` - List available labs
- `/scores <lab>` - Get scores for specific lab

### Task 3: Intent Routing with LLM
- Natural language understanding for queries like "what labs are available"
- Intent classification using Qwen Code API
- Context-aware responses based on student data

### Task 4: Analytics Dashboard
- Submission timeline charts
- Score distribution
- Group performance comparison
- Task pass rates

## Testing Strategy

1. **Unit Tests**: Handler functions tested in isolation with mocked services
2. **Integration Tests**: Full bot flow with test Telegram account
3. **E2E Tests**: Autochecker validates `/start`, `/help`, `/health` commands

## Deployment

- Docker containerization for consistent deployment
- Environment-based configuration (`.env.bot.secret`)
- Process management via `nohup` or systemd on VM
- Health checks via `/health` endpoint

## Future Improvements

- Inline keyboard navigation
- Submission notifications via webhook
- Multi-language support
- Voice message support for accessibility
