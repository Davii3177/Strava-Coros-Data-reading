"""Strava API client.

Strava OAuth flow: https://developers.strava.com/docs/authentication/
"""
import os
from datetime import date, datetime, timedelta

import requests

from models import Run

TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def is_configured() -> bool:
    return bool(
        os.getenv("STRAVA_CLIENT_ID")
        and os.getenv("STRAVA_CLIENT_SECRET")
        and os.getenv("STRAVA_REFRESH_TOKEN")
    )


def fetch_runs(limit: int = 10) -> list[Run]:
    """Returns recent runs. Falls back to sample data until real credentials are set up."""
    if not is_configured():
        return _sample_runs(limit)

    access_token = _get_access_token()
    resp = requests.get(
        ACTIVITIES_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"per_page": limit * 2},  # over-fetch since we filter to runs only
        timeout=10,
    )
    resp.raise_for_status()
    activities = resp.json()

    runs = [_to_run(a) for a in activities if a.get("type") == "Run"]
    return runs[:limit]


def _get_access_token() -> str:
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.getenv("STRAVA_CLIENT_ID"),
            "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
            "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _to_run(activity: dict) -> Run:
    distance_km = activity["distance"] / 1000
    duration_min = activity["moving_time"] / 60
    pace_min_km = duration_min / distance_km if distance_km else 0.0
    return Run(
        id=str(activity["id"]),
        date=datetime.fromisoformat(activity["start_date_local"].rstrip("Z")).date(),
        source="strava",
        distance_km=round(distance_km, 2),
        duration_min=round(duration_min, 1),
        avg_hr=round(activity.get("average_heartrate") or 0),
        avg_pace_min_km=round(pace_min_km, 2),
        elevation_gain_m=round(activity.get("total_elevation_gain") or 0),
    )


def _sample_runs(limit: int) -> list[Run]:
    today = date.today()
    samples = [
        Run("strava-sample-0", today - timedelta(days=1), "strava", 8.05, 42.0, 152, 5.22, 45),
        Run("strava-sample-1", today - timedelta(days=3), "strava", 5.0, 24.5, 161, 4.90, 20),
        Run("strava-sample-2", today - timedelta(days=5), "strava", 12.1, 68.0, 148, 5.62, 110),
        Run("strava-sample-3", today - timedelta(days=8), "strava", 6.5, 31.0, 158, 4.77, 30),
    ]
    return samples[:limit]
