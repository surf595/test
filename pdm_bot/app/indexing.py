import json
import queue
import threading
import time
from pathlib import Path
from typing import Dict, List

from qdrant_client.http import models as rest
from qdrant_client.models import PointStruct

from .config import AUTO_SYNC_SECONDS, DOCS_DIR, EMBED_BATCH_SIZE, QDRANT_COLLECTION, UPSERT_BATCH_SIZE
from .db import (
    create_job,
    delete_index_row,
    get_all_index_rows,
    get_sync_value,
    set_sync_value,
    update_job,
    upsert_index_row,
)
from .documents import extract_chunks
from .llm import embeddings_for_texts
from .retrieval import ensure_qdrant_collection, point_id_for_chunk, qdrant
from .utils import sha1_of_file

_job_queue: "queue.Queue[int]" = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()


def upsert_document_chunks(path: Path, chunks: List[Dict]) -> int:
    file_path = str(path.resolve())
    file_name = path.name

    qdrant.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=rest.FilterSelector(
            filter=rest.Filter(
                must=[rest.FieldCondition(key="source_path", match=rest.MatchValue(value=file_path))]
            )
        ),
    )

    if not chunks:
        return 0

    points = []
    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[start : start + EMBED_BATCH_SIZE]
        vecs = embeddings_for_texts([r["text"] for r in batch])

        for idx_offset, (row, vector) in enumerate(zip(batch, vecs)):
            idx = start + idx_offset
            payload = {
                "source_path": file_path,
                "source_name": file_name,
                "chunk_index": idx,
                **row,
            }
            points.append(PointStruct(id=point_id_for_chunk(file_path, idx), vector=vector, payload=payload))

    for i in range(0, len(points), UPSERT_BATCH_SIZE):
        qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points[i : i + UPSERT_BATCH_SIZE], wait=True)

    return len(chunks)


def sync_library(force: bool = False) -> Dict[str, int]:
    now = time.time()
    last_sync = float(get_sync_value("last_sync_ts", "0") or "0")
    if not force and (now - last_sync) < AUTO_SYNC_SECONDS:
        return {"indexed": 0, "deleted": 0, "skipped": 1}

    ensure_qdrant_collection()
    existing_rows = get_all_index_rows()
    existing_map = {row["file_path"]: row for row in existing_rows}

    files = []
    for ext in ("*.txt", "*.md", "*.pdf", "*.docx"):
        for p in DOCS_DIR.rglob(ext):
            if "originals" not in p.parts:
                files.append(p)

    actual_paths, indexed_count, deleted_count = set(), 0, 0

    for path in files:
        file_path = str(path.resolve())
        actual_paths.add(file_path)
        stat = path.stat()
        sha1 = sha1_of_file(path)
        old = existing_map.get(file_path)

        if old and old["sha1"] == sha1 and float(old["mtime"]) == stat.st_mtime:
            continue

        chunks = extract_chunks(path)
        chunks_count = upsert_document_chunks(path, chunks)
        upsert_index_row(file_path, path.name, sha1, stat.st_mtime, stat.st_size, chunks_count)
        indexed_count += 1

    for row in existing_rows:
        file_path = row["file_path"]
        if file_path not in actual_paths:
            qdrant.delete(
                collection_name=QDRANT_COLLECTION,
                points_selector=rest.FilterSelector(
                    filter=rest.Filter(
                        must=[rest.FieldCondition(key="source_path", match=rest.MatchValue(value=file_path))]
                    )
                ),
            )
            delete_index_row(file_path)
            deleted_count += 1

    set_sync_value("last_sync_ts", str(now))
    return {"indexed": indexed_count, "deleted": deleted_count, "skipped": 0}


def _job_worker() -> None:
    while True:
        job_id = _job_queue.get()
        update_job(job_id, "processing")
        try:
            sync_library(force=True)
            update_job(job_id, "done")
        except Exception as e:
            update_job(job_id, "failed", str(e)[:1000])
        finally:
            _job_queue.task_done()


def start_worker() -> None:
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        t = threading.Thread(target=_job_worker, daemon=True, name="index-worker")
        t.start()
        _worker_started = True


def enqueue_full_reindex(payload: Dict) -> int:
    job_id = create_job("full_reindex", json.dumps(payload, ensure_ascii=False))
    _job_queue.put(job_id)
    return job_id
