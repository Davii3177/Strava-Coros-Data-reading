"""Durable connection and sync-health metadata.

The activity clients still own provider-specific OAuth. This store separates
that secret-bearing work from displayable operational state such as the last
successful sync and the last safe error message.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


def _database_path() -> str:
    # SQLite is the zero-config local fallback. Deployments should point
    # DATABASE_PATH at a mounted persistent disk until the managed Postgres
    # migration is configured.
    return os.environ.get(
        "DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "gaman.sqlite3")
    )


def _postgres_url() -> str | None:
    return os.environ.get("DATABASE_URL") or None


@contextmanager
def _connection():
    postgres_url = _postgres_url()
    if postgres_url:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # clear deployment error, no silent data loss
            raise RuntimeError("DATABASE_URL requires psycopg. Install requirements.txt first.") from exc
        conn = psycopg.connect(postgres_url, row_factory=dict_row)
        placeholder = "%s"
    else:
        path = _database_path()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        placeholder = "?"
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS connection_status (
                provider TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_synced_at TEXT,
                activity_count INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                updated_at TEXT NOT NULL
            )"""
        )
        yield conn, placeholder
        conn.commit()
    finally:
        conn.close()


def record_success(provider: str, activity_count: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connection() as (conn, marker):
        sql = """INSERT INTO connection_status
               (provider, status, last_synced_at, activity_count, last_error, updated_at)
               VALUES (MARKER, 'connected', MARKER, MARKER, NULL, MARKER)
               ON CONFLICT(provider) DO UPDATE SET
                 status='connected', last_synced_at=excluded.last_synced_at,
                 activity_count=excluded.activity_count, last_error=NULL, updated_at=excluded.updated_at"""
        conn.execute(
            sql.replace("MARKER", marker),
            (provider, now, activity_count, now),
        )


def record_failure(provider: str, message: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    safe_message = str(message).replace("\n", " ")[:180]
    with _connection() as (conn, marker):
        sql = """INSERT INTO connection_status
               (provider, status, last_synced_at, activity_count, last_error, updated_at)
               VALUES (MARKER, 'error', NULL, 0, MARKER, MARKER)
               ON CONFLICT(provider) DO UPDATE SET
                 status='error', last_error=excluded.last_error, updated_at=excluded.updated_at"""
        conn.execute(
            sql.replace("MARKER", marker),
            (provider, safe_message, now),
        )


def statuses(configured: dict[str, bool]) -> dict[str, dict]:
    with _connection() as (conn, _):
        rows = {row["provider"]: dict(row) for row in conn.execute("SELECT * FROM connection_status").fetchall()}
    result = {}
    for provider, is_configured in configured.items():
        row = rows.get(provider, {})
        result[provider] = {
            "provider": provider,
            "configured": is_configured,
            "status": row.get("status", "connected" if is_configured else "not_connected"),
            "last_synced_at": row.get("last_synced_at"),
            "activity_count": row.get("activity_count", 0),
            "last_error": row.get("last_error"),
        }
    return result
