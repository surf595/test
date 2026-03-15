from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from .config import TELEGRAM_TOKEN, validate_runtime_config
from .db import init_db
from .health import runtime_health_report
from .indexing import start_worker, sync_library
from .logging_setup import setup_logging
from .retrieval import ensure_qdrant_collection
from .telegram_handlers import (
    collections_command,
    config_command,
    debug_command,
    depth_command,
    diagnose,
    error_handler,
    handle_callback,
    handle_message,
    health_command,
    help_command,
    index_status_command,
    jobs_command,
    mode_command,
    reindex_command,
    sources_command,
    start,
    stats_command,
    tone_command,
)


def main() -> None:
    logger = setup_logging()
    validate_runtime_config()
    init_db()
    ensure_qdrant_collection()
    start_worker()

    try:
        sync_library(force=True)
    except Exception:
        logger.exception("Ошибка стартовой синхронизации")

    try:
        report = runtime_health_report()
        logger.info(
            "Диагностика старта: overall=%s .env=%s TELEGRAM_TOKEN=%s OPENAI_API_KEY=%s DOCS_DIR=%s Qdrant=%s",
            report.get("overall"),
            report.get("env_file"),
            report.get("telegram_token"),
            report.get("openai_api_key"),
            report.get("docs_dir"),
            report.get("qdrant"),
        )
    except Exception:
        logger.exception("Ошибка диагностики старта")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("diagnose", diagnose))
    app.add_handler(CommandHandler("tone", tone_command))
    app.add_handler(CommandHandler("depth", depth_command))
    app.add_handler(CommandHandler("mode", mode_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reindex", reindex_command))
    app.add_handler(CommandHandler("index_status", index_status_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(CommandHandler("collections", collections_command))
    app.add_handler(CommandHandler("jobs", jobs_command))
    app.add_handler(CommandHandler("config", config_command))
    app.add_handler(CommandHandler("debug", debug_command))
    app.add_handler(CommandHandler("sources", sources_command))

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("pdm_bot запущен")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
