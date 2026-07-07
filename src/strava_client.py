"""Strava API client. Real OAuth + fetch logic goes here once credentials are set up.

Strava OAuth flow: https://developers.strava.com/docs/authentication/
"""
import os
from datetime import date, timedelta

from models import Run


def is_configured() -> bool:
    return bool(os.getenv("STRAVA_CLIENT_ID") and os.getenv("STRAVA_REFRESH_TOKEN"))


def fetch_runs(limit: int = 10) -> list[Run]:
    """Returns recent runs. Falls back to sample data until real API integration lands."""
    if not is_configured():
        return _sample_runs(limit)

    # TODO: exchange refresh token for access token, call
    # GET https://www.strava.com/api/v3/athlete/activities, filter type == "Run"
    raise NotImplementedError("Strava API integration not yet implemented")


def _sample_runs(limit: int) -> list[Run]:
    today = date.today()
    samples = [
        Run(today - timedelta(days=1), "strava", 8.05, 42.0, 152, 5.22, 45),
        Run(today - timedelta(days=3), "strava", 5.0, 24.5, 161, 4.90, 20),
        Run(today - timedelta(days=5), "strava", 12.1, 68.0, 148, 5.62, 110),
        Run(today - timedelta(days=8), "strava", 6.5, 31.0, 158, 4.77, 30),
    ]
    return samples[:limit]
