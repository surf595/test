from typing import Dict, List

from ..db import get_library_stats, list_jobs
from ..indexing import enqueue_full_reindex, sync_library


def run_sync(force: bool = False) -> Dict[str, int]:
    return sync_library(force)


def queue_full_reindex(payload: Dict) -> int:
    return enqueue_full_reindex(payload)


def get_recent_jobs(limit: int = 10) -> List:
    return list_jobs(limit)


def get_stats_row():
    return get_library_stats()
