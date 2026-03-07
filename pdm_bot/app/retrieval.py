import hashlib
import re
from typing import Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from .config import MAX_CONTEXT_CHARS, OPENAI_EMBED_DIM, QDRANT_COLLECTION, QDRANT_HOST, QDRANT_PORT, TOP_K
from .llm import embedding_for_text

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
_collection_ensured = False


def point_id_for_chunk(file_path: str, chunk_index: int) -> int:
    raw = f"{file_path}::{chunk_index}".encode("utf-8")
    return int(hashlib.sha1(raw).hexdigest()[:15], 16)


def ensure_qdrant_collection() -> None:
    global _collection_ensured
    if _collection_ensured:
        return
    collections = qdrant.get_collections().collections
    if not any(c.name == QDRANT_COLLECTION for c in collections):
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=OPENAI_EMBED_DIM, distance=Distance.COSINE),
        )
    _collection_ensured = True


def keyword_score(query: str, text: str) -> float:
    q_tokens = {t for t in re.findall(r"\w+", query.lower()) if len(t) > 2}
    if not q_tokens:
        return 0.0
    t_tokens = set(re.findall(r"\w+", text.lower()))
    inter = len(q_tokens.intersection(t_tokens))
    return inter / max(1, len(q_tokens))


def retrieve_context(query: str, top_k: int = TOP_K, domain_scope: str = "all") -> List[Dict]:
    ensure_qdrant_collection()
    query_vector = embedding_for_text(query)
    result = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k * 3,
        with_payload=True,
    )
    hits = result.points if hasattr(result, "points") else []

    rows: List[Dict] = []
    for hit in hits:
        payload = hit.payload or {}
        text = str(payload.get("text", "")).strip()
        if not text:
            continue

        corpus = str(payload.get("corpus", "")).lower()
        if domain_scope not in {"all", "pdm", "group_analysis", "diagnosis"}:
            domain_scope = "all"
        if domain_scope != "all" and domain_scope not in corpus:
            continue

        v_score = float(getattr(hit, "score", 0.0))
        k_score = keyword_score(query, text)
        hybrid = 0.75 * v_score + 0.25 * k_score

        rows.append(
            {
                "hybrid_score": hybrid,
                "vector_score": v_score,
                "keyword_score": k_score,
                "source_name": payload.get("source_name", "unknown"),
                "source_path": payload.get("source_path", ""),
                "chunk_index": payload.get("chunk_index", 0),
                "text": text,
                "author": payload.get("author", ""),
                "title": payload.get("title", ""),
                "year": payload.get("year", ""),
                "language": payload.get("language", ""),
                "section": payload.get("section", ""),
                "chapter": payload.get("chapter", ""),
                "page_start": payload.get("page_start"),
                "page_end": payload.get("page_end"),
            }
        )

    rows.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return rows[:top_k]


def build_context_block(retrieved: List[Dict]) -> Tuple[str, List[str]]:
    used_sources, parts, total_chars = [], [], 0
    for i, item in enumerate(retrieved, start=1):
        src = str(item["source_name"])
        page = ""
        if item.get("page_start"):
            page = f", стр. {item['page_start']}"
        snippet = f"[Источник {i}: {src}{page}]\n{item['text']}\n"
        if total_chars + len(snippet) > MAX_CONTEXT_CHARS:
            break
        parts.append(snippet)
        total_chars += len(snippet)
        if src not in used_sources:
            used_sources.append(src)
    return "\n".join(parts), used_sources
