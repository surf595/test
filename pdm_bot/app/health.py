from pathlib import Path
from typing import Dict

from .config import DOCS_DIR, ENV_PATH, OPENAI_API_KEY, TELEGRAM_TOKEN
from .retrieval import ensure_qdrant_collection, qdrant


def runtime_health_report() -> Dict[str, str]:
    report = {
        "env_file": "доступен" if Path(ENV_PATH).exists() else "отсутствует",
        "telegram_token": "доступен" if TELEGRAM_TOKEN else "отсутствует",
        "openai_api_key": "доступен" if OPENAI_API_KEY else "отсутствует",
        "docs_dir": "доступна" if Path(DOCS_DIR).exists() else "отсутствует",
        "qdrant": "не проверен",
    }

    try:
        ensure_qdrant_collection()
        qdrant.get_collections()
        report["qdrant"] = "доступен"
    except Exception:
        report["qdrant"] = "недоступен"

    ok_values = {"доступен", "доступна"}
    report["overall"] = "норма" if all(v in ok_values for k, v in report.items() if k != "overall") else "деградация"
    return report
