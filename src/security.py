"""Small, dependency-free request security helpers for Gaman."""

import hmac
import secrets
import threading
import time
from collections import defaultdict, deque


class LoginRateLimiter:
    """In-memory sliding-window limiter for password attempts.

    This is intentionally a safety net rather than a substitute for a shared
    production limiter. It keeps a single process from accepting unlimited
    guesses and has no external-service dependency for local development.
    """

    def __init__(self, limit: int = 8, window_seconds: int = 900):
        self.limit = limit
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allowed(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            attempts = self._attempts[key]
            while attempts and now - attempts[0] >= self.window_seconds:
                attempts.popleft()
            return len(attempts) < self.limit

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._attempts[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


def csrf_token(session: dict) -> str:
    """Return a stable, session-bound CSRF token, creating it if necessary."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def csrf_valid(session: dict, submitted: str | None) -> bool:
    expected = session.get("csrf_token")
    return bool(expected and submitted and hmac.compare_digest(expected, submitted))
