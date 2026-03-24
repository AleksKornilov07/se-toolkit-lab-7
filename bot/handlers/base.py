# -*- coding: utf-8 -*-
from services.lms_api import lms_client

async def handle_start() -> str:
    return (
        "👋 Добро пожаловать в LMS Bot!\n\n"
        "Я помогу вам узнать информацию о лабораторных работах, оценках и успеваемости.\n\n"
        "Вы можете спросить меня:\n"
        "• Какие лабораторные доступны?\n"
        "• Какие оценки по lab-01?\n"
        "• У какой лаборатории наименьший процент сдачи?\n"
        "• Кто лучшие студенты в lab-03?\n\n"
        "Или используйте команды: /help, /health, /labs, /scores"
    )

async def handle_help() -> str:
    return (
        "📚 Доступные команды:\n\n"
        "/start — Приветственное сообщение\n"
        "/help — Эта справка\n"
        "/health — Проверка подключения к бэкенду\n"
        "/labs — Список всех лабораторных работ\n"
        "/scores <lab> — Оценки по конкретной лабораторной\n\n"
        "Вы также можете писать вопросы обычным текстом:\n"
        "• \"какие лабораторные доступны?\"\n"
        "• \"покажи оценки по lab-04\"\n"
        "• \"у какой лаборатории наименьший процент сдачи?\""
    )

async def handle_health() -> str:
    try:
        items = await lms_client.get_items()
        return f"✅ Backend healthy. {len(items)} items."
    except Exception as e:
        return f"⚠️ Backend error: {str(e)}"

async def handle_labs() -> str:
    try:
        items = await lms_client.get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        if not labs:
            return "Лабораторные работы не найдены."
        return "📚 Лабораторные работы:\n\n" + "\n".join(
            f"• {l.get('id', 'N/A')} — {l.get('title', 'Без названия')}"
            for l in labs[:20]  # Limit to first 20
        )
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def handle_scores(lab: str = "") -> str:
    if not lab:
        return "⚠️ Укажите лабораторную: /scores lab-01"
    try:
        rates = await lms_client.get_pass_rates(lab)
        if not rates:
            return f"⚠️ Нет данных для {lab}"
        
        lines = [f"📊 Оценки для {lab}:"]
        for task in rates:
            task_name = task.get("task", task.get("id", "N/A"))
            avg_score = task.get("avg_score", task.get("average", 0))
            attempts = task.get("attempts", 0)
            lines.append(f"• {task_name}: {avg_score:.1f}% ({attempts} попыток)")
        
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
