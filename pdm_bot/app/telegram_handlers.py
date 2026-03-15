import asyncio
import time
from typing import List

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from .config import DOCS_DIR, MEMORY_MESSAGES_LIMIT, OWNER_CHAT_ID, TOP_K
from .db import get_sync_value, get_user_row, set_user_setting
from .health import runtime_health_report
from .services.conversation_service import build_assistant_reply
from .services.indexing_service import get_recent_jobs, get_stats_row, queue_full_reindex, run_sync
from .services.user_settings_service import (
    DEPTH_TITLES,
    MODE_TITLES,
    TONE_TITLES,
    depth_keyboard,
    mode_keyboard,
    render_profile,
    tone_keyboard,
)
from .utils import split_message

def _is_owner(chat_id: str) -> bool:
    return bool(OWNER_CHAT_ID) and chat_id == OWNER_CHAT_ID


def _owner_guard(chat_id: str) -> str:
    if _is_owner(chat_id):
        return ""
    return "Эта команда доступна только владельцу бота."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    row = await asyncio.to_thread(get_user_row, str(update.effective_chat.id))
    await update.message.reply_text(
        "Бот запущен.\n\n"
        "Команды:\n"
        "/help /diagnose /tone /depth /mode /stats /reindex /index_status /health /collections /config\n"
        "(админ-команды доступны только владельцу)\n"
        f"{render_profile(row)}",
        reply_markup=mode_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            """Доступные команды:
• /start — запуск и текущие настройки
• /help — помощь
• /diagnose — выбор режима
• /tone — выбор тона
• /depth — выбор глубины
• /mode — показать профиль
• /stats — статистика библиотеки
• /reindex — поставить индексацию в очередь
• /index_status — статус задач индексации

Команды владельца:
• /health • /collections • /config • /jobs • /debug • /sources"""
        )


async def diagnose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Выбери режим:", reply_markup=mode_keyboard())


async def tone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Выбери тон:", reply_markup=tone_keyboard())


async def depth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Выбери глубину:", reply_markup=depth_keyboard())


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return
    row = await asyncio.to_thread(get_user_row, str(update.effective_chat.id))
    await update.message.reply_text(render_profile(row))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    row = await asyncio.to_thread(get_stats_row)
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
    job_id = await asyncio.to_thread(queue_full_reindex, {"chat_id": chat_id})
    await update.message.reply_text(f"Индексация поставлена в очередь. job_id={job_id}")


async def index_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    jobs = await asyncio.to_thread(get_recent_jobs, 10)
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

    sync_res = await asyncio.to_thread(run_sync, False)
    report = await asyncio.to_thread(runtime_health_report)

    text = (
        f"Состояние: {report['overall']}\n"
        f"• .env: {report['env_file']}\n"
        f"• TELEGRAM_TOKEN: {report['telegram_token']}\n"
        f"• OPENAI_API_KEY: {report['openai_api_key']}\n"
        f"• DOCS_DIR: {report['docs_dir']}\n"
        f"• Qdrant: {report['qdrant']}\n"
        f"• Автосинхронизация: {sync_res}"
    )
    await update.message.reply_text(text)


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
    await update.message.reply_text(render_profile(row))


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
        await query.edit_message_text(render_profile(row))
        return

    await query.edit_message_text("Неизвестная настройка")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    user_text = update.message.text.strip()
    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    answer = await asyncio.to_thread(build_assistant_reply, chat_id, user_text, TOP_K, MEMORY_MESSAGES_LIMIT)

    for part in split_message(answer):
        await update.message.reply_text(part)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Необработанная ошибка: {context.error}")
