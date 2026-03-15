import logging
from typing import Dict, List, Tuple

from ..retrieval import build_context_block, retrieve_context

logger = logging.getLogger(__name__)


def retrieve_context_safe(user_text: str, top_k: int, domain_scope: str) -> Tuple[List[Dict], bool]:
    try:
        return retrieve_context(user_text, top_k, domain_scope), False
    except Exception:
        logger.exception("Ошибка retrieval для domain_scope=%s", domain_scope)
        return [], True


def build_context_and_sources(retrieved: List[Dict]) -> Tuple[str, List[str]]:
    return build_context_block(retrieved)
