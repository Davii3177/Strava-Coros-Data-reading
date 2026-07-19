"""Account persistence for the transition away from a shared dashboard password."""

import re
import sqlite3
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from connection_store import _connection

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _execute(conn, marker: str, sql: str, params=()):
    return conn.execute(sql.replace("MARKER", marker), params)


def _ensure(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )


def has_users() -> bool:
    with _connection() as (conn, _):
        _ensure(conn)
        return conn.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None


def create_user(user_id: str, email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    if len(password) < 12:
        return False, "Use a password with at least 12 characters."
    with _connection() as (conn, marker):
        _ensure(conn)
        try:
            _execute(
                conn, marker,
                "INSERT INTO users (id, email, password_hash, created_at) VALUES (MARKER, MARKER, MARKER, MARKER)",
                (user_id, email, generate_password_hash(password), datetime.now(timezone.utc).isoformat()),
            )
        except (sqlite3.IntegrityError, Exception) as exc:
            # PostgreSQL uses a different IntegrityError class; avoid exposing
            # backend detail and distinguish only the expected duplicate case.
            if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
                return False, "An account with that email already exists."
            raise
    return True, email


def authenticate(email: str, password: str) -> dict | None:
    email = email.strip().lower()
    with _connection() as (conn, marker):
        _ensure(conn)
        row = _execute(conn, marker, "SELECT id, email, password_hash FROM users WHERE email = MARKER", (email,)).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return None
    return {"id": row["id"], "email": row["email"]}
