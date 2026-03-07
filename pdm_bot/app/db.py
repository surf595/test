import sqlite3
import threading
from typing import List, Optional

from .config import DB_PATH

db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.row_factory = sqlite3.Row
lock = threading.Lock()

ALLOWED_USER_FIELDS = {
    "mode",
    "tone",
    "depth",
    "response_style",
    "citation_mode",
    "domain_scope",
    "language_pref",
    "verbosity",
    "sources_enabled",
    "debug_enabled",
}


def init_db() -> None:
    with lock:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                chat_id TEXT PRIMARY KEY,
                mode TEXT NOT NULL DEFAULT 'analytic',
                tone TEXT NOT NULL DEFAULT 'attuned',
                depth TEXT NOT NULL DEFAULT 'deep',
                response_style TEXT NOT NULL DEFAULT 'clinical',
                citation_mode TEXT NOT NULL DEFAULT 'sources',
                domain_scope TEXT NOT NULL DEFAULT 'all',
                language_pref TEXT NOT NULL DEFAULT 'auto',
                verbosity TEXT NOT NULL DEFAULT 'medium',
                sources_enabled INTEGER NOT NULL DEFAULT 1,
                debug_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS document_index (
                file_path TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                sha1 TEXT NOT NULL,
                mtime REAL NOT NULL,
                size_bytes INTEGER NOT NULL,
                chunks_count INTEGER NOT NULL DEFAULT 0,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS indexing_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.commit()


def get_user_row(chat_id: str) -> sqlite3.Row:
    with lock:
        row = db.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,)).fetchone()
        if row:
            return row
        db.execute("INSERT INTO users (chat_id) VALUES (?)", (chat_id,))
        db.commit()
        return db.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,)).fetchone()


def set_user_setting(chat_id: str, field: str, value) -> None:
    if field not in ALLOWED_USER_FIELDS:
        raise ValueError(f"Недопустимое поле: {field}")

    with lock:
        db.execute(
            f"""
            INSERT INTO users (chat_id, {field}, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(chat_id) DO UPDATE SET
                {field}=excluded.{field},
                updated_at=CURRENT_TIMESTAMP
            """,
            (chat_id, value),
        )
        db.commit()


def get_sync_value(key: str, default: str = "") -> str:
    with lock:
        row = db.execute("SELECT value FROM sync_state WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_sync_value(key: str, value: str) -> None:
    with lock:
        db.execute(
            """
            INSERT INTO sync_state (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value),
        )
        db.commit()


def save_message(chat_id: str, role: str, content: str) -> None:
    with lock:
        db.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content),
        )
        db.commit()


def get_recent_messages(chat_id: str, limit: int = 12) -> List[sqlite3.Row]:
    with lock:
        rows = db.execute(
            """
            SELECT role, content, created_at FROM messages
            WHERE chat_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (chat_id, limit),
        ).fetchall()
    return list(reversed(rows))


def create_job(job_type: str, payload: str = "") -> int:
    with lock:
        cur = db.execute(
            "INSERT INTO indexing_jobs (job_type, status, payload) VALUES (?, 'queued', ?)",
            (job_type, payload),
        )
        db.commit()
        return int(cur.lastrowid)


def update_job(job_id: int, status: str, error: str = "") -> None:
    with lock:
        db.execute(
            """
            UPDATE indexing_jobs
            SET status=?, error=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (status, error, job_id),
        )
        db.commit()


def list_jobs(limit: int = 10) -> List[sqlite3.Row]:
    with lock:
        return db.execute(
            """
            SELECT id, job_type, status, error, created_at, updated_at
            FROM indexing_jobs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def get_library_stats() -> sqlite3.Row:
    with lock:
        return db.execute(
            "SELECT COUNT(*) AS docs_count, COALESCE(SUM(chunks_count), 0) AS chunks_count FROM document_index"
        ).fetchone()


def get_all_index_rows() -> List[sqlite3.Row]:
    with lock:
        return db.execute("SELECT * FROM document_index").fetchall()


def upsert_index_row(file_path: str, file_name: str, sha1: str, mtime: float, size_bytes: int, chunks_count: int) -> None:
    with lock:
        db.execute(
            """
            INSERT INTO document_index (file_path, file_name, sha1, mtime, size_bytes, chunks_count, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_path) DO UPDATE SET
                file_name=excluded.file_name,
                sha1=excluded.sha1,
                mtime=excluded.mtime,
                size_bytes=excluded.size_bytes,
                chunks_count=excluded.chunks_count,
                indexed_at=CURRENT_TIMESTAMP
            """,
            (file_path, file_name, sha1, mtime, size_bytes, chunks_count),
        )
        db.commit()


def delete_index_row(file_path: str) -> None:
    with lock:
        db.execute("DELETE FROM document_index WHERE file_path=?", (file_path,))
        db.commit()
