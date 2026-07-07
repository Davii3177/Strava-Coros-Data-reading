"""Coros API client. Real auth + fetch logic goes here once credentials/endpoint are confirmed.

Coros does not have a fully public API like Strava; this will likely use the
Coros training hub API or a community client once selected.
"""
import os
from datetime import date, timedelta

from models import Run


def is_configured() -> bool:
    return bool(os.getenv("COROS_CLIENT_ID") and os.getenv("COROS_CLIENT_SECRET"))


def fetch_runs(limit: int = 10) -> list[Run]:
    """Returns recent runs. Falls back to sample data until real API integration lands."""
    if not is_configured():
        return _sample_runs(limit)

    raise NotImplementedError("Coros API integration not yet implemented")


def _sample_runs(limit: int) -> list[Run]:
    today = date.today()
    samples = [
        Run(today - timedelta(days=2), "coros", 10.0, 52.0, 155, 5.20, 60),
        Run(today - timedelta(days=6), "coros", 4.2, 19.5, 165, 4.64, 15),
    ]
    return samples[:limit]
