import re
import sqlite3
from typing import Dict

MODE_PROMPTS = {
    "analytic": "Сохраняй аналитическую позицию и работай через гипотезы.",
    "diagnostic": "Работай как психодинамически ориентированный диагностический ассистент, без финальных диагнозов.",
    "supportive": "Будь поддерживающим, контейнирующим, с фокусом на переживания.",
    "general": "Отвечай ясно и по существу.",
}

TONE_PROMPTS = {
    "attuned": "Пиши с чуткостью.",
    "neutral": "Пиши нейтрально.",
    "structured": "Пиши структурно.",
    "warm": "Пиши тепло и человечно, с границами.",
}

DEPTH_PROMPTS = {
    "brief": "Короткий ответ.",
    "medium": "Средняя детализация.",
    "deep": "Глубокий многослойный ответ.",
}

STYLE_PROMPTS = {
    "clinical": "Стиль: клинический.",
    "human": "Стиль: человеческий, доступный.",
    "educational": "Стиль: учебный, с объяснением терминов.",
    "supervisory": "Стиль: супервизионный, с гипотезами и альтернативами.",
}


def detect_language_hint(text: str, language_pref: str) -> str:
    if language_pref in {"ru", "en"}:
        return "Отвечай по-русски." if language_pref == "ru" else "Отвечай по-английски."

    cyr = len(re.findall(r"[А-Яа-яЁё]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    if cyr > lat:
        return "Отвечай по-русски."
    if lat > cyr:
        return "Отвечай на том же языке, что и пользователь."
    return "Отвечай на языке пользователя."


def route_task_type(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["что такое", "определи", "definition", "термин"]):
        return "definition"
    if any(x in t for x in ["сравни", "difference", "vs", "отлич"]):
        return "comparison"
    if any(x in t for x in ["клиент", "пациент", "случай", "case"]):
        return "clinical"
    if any(x in t for x in ["источник", "книга", "author", "цитата", "страниц"]):
        return "bibliography"
    return "general"


def task_instruction(task: str) -> str:
    mapping: Dict[str, str] = {
        "definition": "Сначала коротко определи термин, затем дай 2–3 уточнения.",
        "comparison": "Сделай сравнительный ответ по пунктам.",
        "clinical": "Сохраняй супервизионную позицию: гипотезы, риски, следующий шаг.",
        "bibliography": "Сделай ответ с явной опорой на найденные источники.",
        "general": "Дай практичный и аккуратный ответ.",
    }
    return mapping[task]


def build_system_prompt(user_row: sqlite3.Row, user_text: str) -> str:
    mode = user_row["mode"]
    tone = user_row["tone"]
    depth = user_row["depth"]
    response_style = user_row["response_style"]
    citation_mode = user_row["citation_mode"]
    domain_scope = user_row["domain_scope"]
    language_pref = user_row["language_pref"]
    verbosity = user_row["verbosity"]

    task = route_task_type(user_text)

    return (
        "Ты — психодинамически ориентированный ассистент.\n"
        f"{detect_language_hint(user_text, language_pref)}\n"
        f"{MODE_PROMPTS.get(mode, MODE_PROMPTS['analytic'])}\n"
        f"{TONE_PROMPTS.get(tone, TONE_PROMPTS['attuned'])}\n"
        f"{DEPTH_PROMPTS.get(depth, DEPTH_PROMPTS['deep'])}\n"
        f"{STYLE_PROMPTS.get(response_style, STYLE_PROMPTS['clinical'])}\n"
        f"Область корпуса: {domain_scope}.\n"
        f"Режим цитирования: {citation_mode}.\n"
        f"Детализация: {verbosity}.\n"
        f"Тип задачи: {task}. {task_instruction(task)}\n"
        "Правила: не выдумывай источники, не ставь окончательных диагнозов, отделяй факты от гипотез."
    )
