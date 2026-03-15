from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "docs"
DB_PATH = BASE_DIR / "bot.db"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_EMBED_DIM = int(os.getenv("OPENAI_EMBED_DIM", "1536"))

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "pdm_library")

OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "")

AUTO_SYNC_SECONDS = int(os.getenv("AUTO_SYNC_SECONDS", "120"))
TOP_K = int(os.getenv("TOP_K", "6"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
UPSERT_BATCH_SIZE = int(os.getenv("UPSERT_BATCH_SIZE", "32"))
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "32"))
MEMORY_MESSAGES_LIMIT = int(os.getenv("MEMORY_MESSAGES_LIMIT", "12"))

DOCS_DIR.mkdir(parents=True, exist_ok=True)


def validate_runtime_config() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не найден в .env")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не найден в .env")
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError("CHUNK_OVERLAP должен быть меньше CHUNK_SIZE")
    if OPENAI_EMBED_DIM <= 0:
        raise ValueError("OPENAI_EMBED_DIM должен быть положительным")
