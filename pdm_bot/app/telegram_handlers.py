import asyncio
import time
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from .config import DOCS_DIR, MEMORY_MESSAGES_LIMIT, OWNER_CHAT_ID, TOP_K
from .db import (
    get_library_stats,
    get_recent_messages,
    get_sync_value,
    get_user_row,
    list_jobs,
    save_message,
    set_user_setting,
)
from .indexing import enqueue_full_reindex, sync_library
from .llm import ask_llm
from .prompts import build_system_prompt
from .retrieval import build_context_block, retrieve_context
from .utils import split_message

MODE_TITLES = {"analytic": "Аналитический", "diagnostic": "Диагностический", "supportive": "Поддерживающий", "general": "Общий"}
TONE_TITLES = {"attuned": "Чуткий", "neutral": "Нейтральный", "structured": "Структурный", "warm": "Тёплый"}
DEPTH_TITLES = {"brief": "Кратко", "medium": "Средне", "deep": "Глубоко"}
DOMAIN_SCOPE_TITLES = {
    "all": "Вся библиотека",
    "pdm": "Только PDM",
    "group_analysis": "Только группанализ",
    "diagnosis": "Только диагностика",
}


def _is_owner(chat_id: str) -> bool:
    return bool(OWNER_CHAT_ID) and chat_id == OWNER_CHAT_ID


def _owner_guard(chat_id: str) -> str:
    if _is_owner(chat_id):
        return ""
    return "Эта команда доступна только владельцу бота."


def _render_profile(user_row) -> str:
    return (
        "Текущие настройки:\n"
        f"• режим: {MODE_TITLES.get(user_row['mode'], user_row['mode'])}\n"
        f"• тон: {TONE_TITLES.get(user_row['tone'], user_row['tone'])}\n"
        f"• глубина: {DEPTH_TITLES.get(user_row['depth'], user_row['depth'])}\n"
        f"• стиль: {user_row['response_style']}\n"
        f"• цитирования: {user_row['citation_mode']}\n"
        f"• область поиска: {DOMAIN_SCOPE_TITLES.get(user_row['domain_scope'], user_row['domain_scope'])}\n"
        f"• язык: {user_row['language_pref']}\n"
        f"• детализация: {user_row['verbosity']}\n"
        f"• источники/отладка: {user_row['sources_enabled']}/{user_row['debug_enabled']}\n"
    )


def _mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Аналитический", callback_data="mode:analytic"), InlineKeyboardButton("Диагностический", callback_data="mode:diagnostic")],
        [InlineKeyboardButton("Поддерживающий", callback_data="mode:supportive"), InlineKeyboardButton("Общий", callback_data="mode:general")],
    ])


def _tone_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Чуткий", callback_data="tone:attuned"), InlineKeyboardButton("Нейтральный", callback_data="tone:neutral")],
        [InlineKeyboardButton("Структурный", callback_data="tone:structured"), InlineKeyboardButton("Тёплый", callback_data="tone:warm")],
    ])


def _depth_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Кратко", callback_data="depth:brief"), InlineKeyboardButton("Средне", callback_data="depth:medium"), InlineKeyboardButton("Глубоко", callback_data="depth:deep")]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    row = await asyncio.to_thread(get_user_row, str(update.effective_chat.id))
    await update.message.reply_text(
        "Бот запущен.\n\n"
        "Команды:\n"
        "/help /diagnose /tone /depth /mode /stats /reindex /index_status /health /collections /config\n"
        "(админ-команды доступны только владельцу)\n"
        f"{_render_profile(row)}",
        reply_markup=_mode_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("/start /help /diagnose /tone /depth /mode /stats /reindex /index_status\nдля владельца: /health /collections /config /jobs /debug /sources")


async def diagnose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Выбери режим:", reply_markup=_mode_keyboard())


async def tone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Выбери тон:", reply_markup=_tone_keyboard())


async def depth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Выбери глубину:", reply_markup=_depth_keyboard())


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    row = await asyncio.to_thread(get_user_row, str(update.effective_chat.id))
    await update.message.reply_text(_render_profile(row))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    row = await asyncio.to_thread(get_library_stats)
    last_sync = await asyncio.to_thread(get_sync_value, "last_sync_ts", "0")
    try:
        last_sync_text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(last_sync)))
    except Exception:
        last_sync_text = "неизвестно"
    await update.message.reply_text(
        f"Библиотека:\n• документов: {row['docs_count']}\n• чанков: {row['chunks_count']}\n• папка: {DOCS_DIR}\n• последняя синхронизация: {last_sync_text}"
    )


async def reindex_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    chat_id = str(update.effective_chat.id)
    guard = _owner_guard(chat_id)
    if guard:
        await update.message.reply_text(guard)
        return
    job_id = await asyncio.to_thread(enqueue_full_reindex, {"chat_id": chat_id})
    await update.message.reply_text(f"Индексация поставлена в очередь. job_id={job_id}")


async def index_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    jobs = await asyncio.to_thread(list_jobs, 10)
    if not jobs:
        await update.message.reply_text("Задач индексации пока нет.")
        return
    text = "\n".join([f"#{j['id']} {j['job_type']} {j['status']} ({j['updated_at']})" for j in jobs])
    await update.message.reply_text(text)


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    guard = _owner_guard(str(update.effective_chat.id))
    if guard:
        await update.message.reply_text(guard)
        return
    res = await asyncio.to_thread(sync_library, False)
    await update.message.reply_text(f"Состояние: OK\nАвтосинхронизация: {res}")


async def collections_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    guard = _owner_guard(str(update.effective_chat.id))
    if guard:
        await update.message.reply_text(guard)
        return
    from .retrieval import qdrant

    cols = await asyncio.to_thread(qdrant.get_collections)
    names = [c.name for c in cols.collections]
    await update.message.reply_text("Коллекции:\n" + "\n".join(f"- {n}" for n in names))


async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await index_status_command(update, context)


async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    row = await asyncio.to_thread(get_user_row, str(update.effective_chat.id))
    await update.message.reply_text(_render_profile(row))


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    guard = _owner_guard(str(update.effective_chat.id))
    if guard:
        await update.message.reply_text(guard)
        return

    args: List[str] = context.args or []
    if not args or args[0] not in {"on", "off"}:
        await update.message.reply_text("Использование: /debug on|off")
        return
    val = 1 if args[0] == "on" else 0
    await asyncio.to_thread(set_user_setting, str(update.effective_chat.id), "debug_enabled", val)
    await update.message.reply_text(f"Режим отладки: {'вкл' if args[0] == 'on' else 'выкл'}")


async def sources_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    args: List[str] = context.args or []
    if not args or args[0] not in {"on", "off"}:
        await update.message.reply_text("Использование: /sources on|off")
        return
    val = 1 if args[0] == "on" else 0
    await asyncio.to_thread(set_user_setting, str(update.effective_chat.id), "sources_enabled", val)
    await update.message.reply_text(f"Показ источников: {'вкл' if args[0] == 'on' else 'выкл'}")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not update.effective_chat:
        return

    await query.answer()
    chat_id = str(update.effective_chat.id)
    data = query.data or ""
    if ":" not in data:
        await query.edit_message_text("Неизвестное действие")
        return

    kind, value = data.split(":", 1)
    allowed = {"mode": MODE_TITLES, "tone": TONE_TITLES, "depth": DEPTH_TITLES}
    if kind in allowed and value in allowed[kind]:
        await asyncio.to_thread(set_user_setting, chat_id, kind, value)
        row = await asyncio.to_thread(get_user_row, chat_id)
        await query.edit_message_text(_render_profile(row))
        return

    await query.edit_message_text("Неизвестная настройка")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    user_text = update.message.text.strip()
    if not user_text:
        return

    await asyncio.to_thread(save_message, chat_id, "user", user_text)
    row = await asyncio.to_thread(get_user_row, chat_id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    history_rows = await asyncio.to_thread(get_recent_messages, chat_id, MEMORY_MESSAGES_LIMIT)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows if r["role"] in {"user", "assistant"}]

    retrieved = await asyncio.to_thread(retrieve_context, user_text, TOP_K, row["domain_scope"])
    context_block, used_sources = build_context_block(retrieved)
    system_prompt = build_system_prompt(row, user_text)

    answer = await asyncio.to_thread(ask_llm, system_prompt, context_block, history, user_text)
    await asyncio.to_thread(save_message, chat_id, "assistant", answer)

    show_sources = int(row["sources_enabled"]) == 1
    if show_sources and used_sources:
        sources_text = "\n".join(f"— {name}" for name in used_sources[:8])
        answer = f"{answer}\n\nИсточники:\n{sources_text}"

    for part in split_message(answer):
        await update.message.reply_text(part)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Необработанная ошибка: {context.error}")
