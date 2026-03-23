# -*- coding: utf-8 -*-
from services.lms_api import lms_client

async def handle_start() -> str:
    return "Welcome to the LMS Bot!"

async def handle_help() -> str:
    return "Commands: /start, /help, /health, /labs, /scores"

async def handle_health() -> str:
    try:
        items = await lms_client.get_items()
        return f"Backend healthy. {len(items)} items."
    except Exception as e:
        return f"Backend error: {str(e)}"

async def handle_labs() -> str:
    try:
        items = await lms_client.get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        return "Labs: " + ", ".join(l.get("title", "") for l in labs)
    except Exception as e:
        return f"Error: {str(e)}"

async def handle_scores(lab: str = "") -> str:
    if not lab:
        return "Specify lab: /scores lab-01"
    try:
        rates = await lms_client.get_pass_rates(lab)
        return f"Scores for {lab}: {len(rates)} tasks"
    except Exception as e:
        return f"Error: {str(e)}"
