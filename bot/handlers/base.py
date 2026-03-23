# -*- coding: utf-8 -*-
from services.lms_api import lms_client

async def handle_start() -> str:
    return "Welcome to the LMS Bot!"

async def handle_help() -> str:
    lines = [
        "Commands:",
        "/start - Welcome message",
        "/help - Show this help",
        "/health - Check backend status",
        "/labs - List available labs",
        "/scores [lab] - Get scores",
    ]
    return chr(10).join(lines)

async def handle_health() -> str:
    try:
        items = await lms_client.get_items()
        return f"Backend is healthy. {len(items)} items available."
    except Exception:
        return "Backend error: connection refused."

async def handle_labs() -> str:
    try:
        items = await lms_client.get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        lines = ["Available Labs:"]
        for l in labs:
            lines.append("- " + l.get("title", ""))
        return chr(10).join(lines)
    except Exception as e:
        return f"Error: {e}"

async def handle_scores(lab: str = "") -> str:
    if not lab:
        return "Specify lab: /scores lab-01"
    try:
        rates = await lms_client.get_pass_rates(lab)
        if not rates:
            return f"No scores for {lab}"
        lines = [f"Pass rates for {lab}:"]
        for task in rates:
            name = task.get("task", task.get("title", ""))
            rate = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"- {name}: {rate:.1f}% ({attempts} attempts)")
        return chr(10).join(lines)
    except Exception as e:
        return f"Error: {e}"
