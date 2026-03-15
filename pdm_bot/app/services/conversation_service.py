import logging
from typing import Dict, List

from ..db import get_recent_messages, get_user_row, save_message
from ..llm import ask_llm
from ..prompts import build_system_prompt
from .retrieval_service import build_context_and_sources, retrieve_context_safe

logger = logging.getLogger(__name__)


def _history_for_chat(chat_id: str, memory_messages_limit: int) -> List[Dict[str, str]]:
    history_rows = get_recent_messages(chat_id, memory_messages_limit)
    return [
        {"role": row["role"], "content": row["content"]}
        for row in history_rows
        if row["role"] in {"user", "assistant"}
    ]


def build_assistant_reply(chat_id: str, user_text: str, top_k: int, memory_messages_limit: int) -> str:
    """Build assistant answer with graceful degradation for retrieval and generation failures."""
    save_message(chat_id, "user", user_text)
    user_row = get_user_row(chat_id)
    history = _history_for_chat(chat_id, memory_messages_limit)

    retrieved, retrieval_error = retrieve_context_safe(user_text, top_k, user_row["domain_scope"])
    context_block, used_sources = build_context_and_sources(retrieved)
    system_prompt = build_system_prompt(user_row, user_text)

    generation_error = False
    answer = ""
    try:
        answer = ask_llm(system_prompt, context_block, history, user_text)
    except Exception:
        generation_error = True
        logger.exception("Ошибка генерации ответа для chat_id=%s", chat_id)
        answer = (
            "Сейчас не удалось сформировать полноценный ответ. "
            "Проверьте доступность OpenAI и повторите запрос чуть позже."
        )

    if int(user_row["sources_enabled"]) == 1 and used_sources:
        sources_text = "\n".join(f"— {name}" for name in used_sources[:8])
        answer = f"{answer}\n\nИсточники:\n{sources_text}"

    if int(user_row["debug_enabled"]) == 1:
        notes = []
        if retrieval_error:
            notes.append("retrieval=ошибка")
        if generation_error:
            notes.append("generation=ошибка")
        if notes:
            answer = f"{answer}\n\n[debug] {'; '.join(notes)}"

    save_message(chat_id, "assistant", answer)
    return answer
