"""Fitbit data source, via the Google Health API.

Google is retiring the legacy Fitbit Web API (dev.fitbit.com) in September 2026
and replacing it with the Google Health API, which authenticates with standard
Google OAuth 2.0 and serves data from a Fitbit device under the "exercise" data
type. This module talks to that new API but keeps the app-facing source label
"fitbit", since from the runner's perspective the data still comes from Fitbit.

Migration reference: https://developers.google.com/health/migration
Exercise data type:   https://developers.google.com/health/reference/rest/v4/users.dataTypes.dataPoints

Credentials are a Google Cloud OAuth 2.0 client (…apps.googleusercontent.com),
not a Fitbit app — see README "Connecting Fitbit (Google Health API)".

The _to_run mapping was verified against a live exercise dataPoint: summary
metrics live under exercise.metricsSummary (distanceMillimeters, and
averageHeartRateBeatsPerMinute as a string), timing under exercise.interval
(startTime/endTime in UTC + startUtcOffset), and moving time in activeDuration.
_find still resolves keys recursively so the mapping tolerates minor shape
changes; distances/elevation are in millimeters.
"""
import os
import time
from datetime import date, datetime, timedelta

import requests

from models import DailyValue, Run, SleepNight

TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_POINTS_URL = "https://health.googleapis.com/v4/users/me/dataTypes/exercise/dataPoints"
DATA_TYPE_URL = "https://health.googleapis.com/v4/users/me/dataTypes/{data_type}/dataPoints"

# millimeter-based units the Google Health API reports distances/elevation in
MM_PER_KM = 1_000_000
MM_PER_M = 1_000


def is_configured() -> bool:
    return bool(
        os.getenv("GOOGLE_HEALTH_CLIENT_ID")
        and os.getenv("GOOGLE_HEALTH_CLIENT_SECRET")
        and os.getenv("GOOGLE_HEALTH_REFRESH_TOKEN")
    )


def fetch_runs(limit: int = 10) -> list[Run]:
    """Returns recent runs. Falls back to sample data until real credentials are set up."""
    if not is_configured():
        return _sample_runs(limit)

    access_token = _get_access_token()
    resp = requests.get(
        DATA_POINTS_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        # No server-side date filter: the exact `filter` value format for
        # exercise.interval.civil_start_time isn't documented publicly, so we
        # over-fetch a recent page and sort/trim client-side to avoid a fragile
        # 400. Switch to `params={"filter": ...}` once the format is confirmed.
        params={"pageSize": min(limit * 5, 100)},
        timeout=10,
    )
    resp.raise_for_status()
    data_points = resp.json().get("dataPoints", [])

    runs = [_to_run(dp) for dp in data_points if _is_run(dp)]
    # Fitbit sometimes tags a no-distance activity (e.g. a 50 m "run") as a run;
    # without a real distance it yields a nonsense pace, so drop those.
    runs = [r for r in runs if r.distance_km >= 0.3]
    runs.sort(key=lambda r: r.date, reverse=True)
    return runs[:limit]


_token_cache = {"token": None, "expires_at": 0.0}


def _get_access_token() -> str:
    # Google refresh tokens do not rotate on use (unlike the legacy Fitbit API),
    # so there is nothing to persist back here — one stored refresh token keeps
    # minting access tokens until the user revokes it or it expires (see README
    # on the 7-day expiry for apps still in OAuth "Testing" status). Access
    # tokens last ~1h, so cache one to avoid re-refreshing on every fetch (a
    # single recovery page pulls runs + sleep + resting HR + HRV).
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.getenv("GOOGLE_HEALTH_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_HEALTH_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_HEALTH_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    return _token_cache["token"]


def _get_points(data_type: str, limit: int) -> list[dict]:
    """List recent dataPoints for a Google Health data type (e.g. "sleep")."""
    access_token = _get_access_token()
    resp = requests.get(
        DATA_TYPE_URL.format(data_type=data_type),
        headers={"Authorization": f"Bearer {access_token}"},
        params={"pageSize": min(limit * 2, 100)},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("dataPoints", [])


def _source_label(dp: dict) -> str:
    """Friendly label for the device/app that recorded a dataPoint."""
    ds = dp.get("dataSource", {}) or {}
    pkg = str((ds.get("application") or {}).get("packageName") or "").lower()
    platform = str(ds.get("platform") or "")
    if "coros" in pkg:
        return "Coros"
    if "fitbit" in pkg or platform == "FITBIT":
        return "Fitbit"
    if "garmin" in pkg:
        return "Garmin"
    return platform.replace("_", " ").title() or "Device"


def _find(obj, *candidate_keys):
    """First scalar value whose key matches any candidate, searched recursively.

    The exercise payload nests leaf values (distanceMillimeters, avgHeartRate,
    civilStartTime, ...) inside exercise / exerciseMetadata / interval, and the
    exact nesting isn't fully documented yet, so a recursive scan keeps the
    mapping working across minor shape differences.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in candidate_keys and not isinstance(value, (dict, list)):
                return value
        for value in obj.values():
            found = _find(value, *candidate_keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find(item, *candidate_keys)
            if found is not None:
                return found
    return None


def _is_run(dp: dict) -> bool:
    ex_type = str(_find(dp, "exerciseType", "type") or "")
    return "run" in ex_type.lower()


def _num(value) -> float:
    """Coerce a value to float. The Google Health API returns several numeric
    summary fields as JSON strings, e.g. averageHeartRateBeatsPerMinute: "114"."""
    if value is None or isinstance(value, bool):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _parse_dt(value) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.rstrip("Z"))
    except ValueError:
        return None


def _offset_date(dt: datetime | None, offset) -> date | None:
    """Apply a UTC offset string (e.g. "-14400s") to a UTC datetime and return
    the local calendar date. Google Health reports times as UTC + a *UtcOffset."""
    if dt is None:
        return None
    if isinstance(offset, str) and offset.endswith("s"):
        return (dt + timedelta(seconds=_num(offset[:-1]))).date()
    return dt.date()


def _local_date(dp: dict, start_utc: datetime | None) -> date:
    """Local calendar day a run belongs to, from interval.startTime + offset."""
    return _offset_date(start_utc, _find(dp, "startUtcOffset")) or datetime.now().date()


def _duration_min(dp: dict, start: datetime | None, end: datetime | None) -> float:
    # Prefer activeDuration (moving time, e.g. "3172s"), matching Strava's
    # moving_time; fall back to the interval's elapsed wall-clock time.
    raw = _find(dp, "activeDuration", "duration")
    if isinstance(raw, str) and raw.endswith("s"):
        secs = _num(raw[:-1])
        if secs:
            return secs / 60
    elif isinstance(raw, (int, float)):
        return raw / 60
    if start and end:
        return (end - start).total_seconds() / 60
    return 0.0


def _to_run(dp: dict) -> Run:
    # Verified against a live Fitbit/Google Health exercise dataPoint: leaf
    # values live under exercise.metricsSummary (distanceMillimeters,
    # averageHeartRateBeatsPerMinute) and exercise.interval (startTime/endTime).
    start = _parse_dt(_find(dp, "startTime", "civilStartTime"))
    end = _parse_dt(_find(dp, "endTime", "civilEndTime"))
    distance_km = _num(_find(dp, "distanceMillimeters", "distance")) / MM_PER_KM
    duration_min = _duration_min(dp, start, end)
    pace_min_km = duration_min / distance_km if distance_km else 0.0
    return Run(
        id=str(_find(dp, "name", "dataPointId") or f"fitbit-{_local_date(dp, start)}"),
        date=_local_date(dp, start),
        source="fitbit",
        distance_km=round(distance_km, 2),
        duration_min=round(duration_min, 1),
        avg_hr=round(_num(_find(dp, "averageHeartRateBeatsPerMinute", "avgHeartRate",
                                "averageHeartRate", "averageHeartRateBpm"))),
        avg_pace_min_km=round(pace_min_km, 2),
        elevation_gain_m=round(_num(_find(dp, "elevationGainMillimeters")) / MM_PER_M),
    )


def _sample_runs(limit: int) -> list[Run]:
    today = date.today()
    samples = [
        Run("fitbit-sample-0", today - timedelta(days=2), "fitbit", 7.2, 38.0, 149, 5.28, 40),
        Run("fitbit-sample-1", today - timedelta(days=5), "fitbit", 3.5, 17.0, 158, 4.86, 12),
    ]
    return samples[:limit]


# ---------------------------------------------------------------------------
# Recovery metrics: sleep, resting heart rate, HRV.
# Verified against live "sleep" and "daily-resting-heart-rate" dataPoints
# (which, via Google Health, may come from a Coros/Fitbit/other device). HRV
# is best-effort: the path resolves but the schema is unverified (no data in
# the account under test), so it degrades to an empty list rather than guess.
# ---------------------------------------------------------------------------

_STAGE_BUCKET = {"DEEP": "deep_min", "REM": "rem_min", "LIGHT": "light_min", "AWAKE": "awake_min"}


def fetch_sleep(limit: int = 7) -> list[SleepNight]:
    if not is_configured():
        return []
    nights = [_to_sleep(p) for p in _get_points("sleep", limit)]
    nights = [n for n in nights if n.in_bed_min > 0]
    nights.sort(key=lambda n: n.date, reverse=True)
    return nights[:limit]


def _to_sleep(dp: dict) -> SleepNight:
    sleep = dp.get("sleep", {}) or {}
    interval = sleep.get("interval", {}) or {}
    start = _parse_dt(interval.get("startTime"))
    end = _parse_dt(interval.get("endTime"))
    in_bed_min = (end - start).total_seconds() / 60 if start and end else 0.0
    buckets = {"deep_min": 0.0, "rem_min": 0.0, "light_min": 0.0, "awake_min": 0.0}
    for stage in sleep.get("stages", []) or []:
        s, e = _parse_dt(stage.get("startTime")), _parse_dt(stage.get("endTime"))
        bucket = _STAGE_BUCKET.get(str(stage.get("type", "")).upper())
        if s and e and bucket:
            buckets[bucket] += (e - s).total_seconds() / 60
    asleep = buckets["deep_min"] + buckets["rem_min"] + buckets["light_min"]
    wake_date = _offset_date(end, interval.get("endUtcOffset")) or date.today()
    return SleepNight(
        id=str(dp.get("name") or f"sleep-{wake_date}"),
        date=wake_date,
        start=start or datetime.now(),
        end=end or datetime.now(),
        in_bed_min=round(in_bed_min, 1),
        asleep_min=round(asleep, 1),
        deep_min=round(buckets["deep_min"], 1),
        rem_min=round(buckets["rem_min"], 1),
        light_min=round(buckets["light_min"], 1),
        awake_min=round(buckets["awake_min"], 1),
        source=_source_label(dp),
    )


def fetch_resting_hr(limit: int = 14) -> list[DailyValue]:
    if not is_configured():
        return []
    values = [v for v in (_to_daily_hr(p) for p in _get_points("daily-resting-heart-rate", limit)) if v]
    values.sort(key=lambda v: v.date, reverse=True)
    return values[:limit]


def _to_daily_hr(dp: dict) -> DailyValue | None:
    rec = dp.get("dailyRestingHeartRate", {}) or {}
    the_date = _ymd_to_date(rec.get("date"))
    bpm = _num(rec.get("beatsPerMinute"))
    if the_date is None or bpm <= 0:
        return None
    return DailyValue(the_date, round(bpm), _source_label(dp))


def fetch_hrv(limit: int = 14) -> list[DailyValue]:
    if not is_configured():
        return []
    for data_type in ("heart-rate-variability", "daily-heart-rate-variability"):
        try:
            points = _get_points(data_type, limit)
        except requests.RequestException:
            continue
        values = [v for v in (_to_hrv(p) for p in points) if v]
        if values:
            values.sort(key=lambda v: v.date, reverse=True)
            return values[:limit]
    return []


def _to_hrv(dp: dict) -> DailyValue | None:
    payload = dp.get("heartRateVariability") or dp.get("dailyHeartRateVariability") or {}
    ms = _num(_find(payload, "rmssdMilliseconds", "rmssd", "milliseconds", "value"))
    the_date = _ymd_to_date(payload.get("date")) or _offset_date(
        _parse_dt(_find(payload, "startTime")), _find(payload, "startUtcOffset"))
    if the_date is None or ms <= 0:
        return None
    return DailyValue(the_date, round(ms, 1), _source_label(dp))


def _ymd_to_date(ymd) -> date | None:
    if not isinstance(ymd, dict):
        return None
    try:
        return date(int(ymd["year"]), int(ymd["month"]), int(ymd["day"]))
    except (KeyError, ValueError, TypeError):
        return None


def _sample_sleep(limit: int) -> list[SleepNight]:
    today = date.today()
    specs = [(85, 95, 262, 20), (65, 80, 240, 25), (78, 92, 250, 28)]
    out = []
    for i, (deep, rem, light, awake) in enumerate(specs):
        wake = today - timedelta(days=i + 1)
        end = datetime.combine(wake, datetime.min.time()) + timedelta(hours=7)
        start = end - timedelta(minutes=deep + rem + light + awake)
        out.append(SleepNight(
            f"sleep-sample-{i}", wake, start, end,
            float(deep + rem + light + awake), float(deep + rem + light),
            float(deep), float(rem), float(light), float(awake), "Sample"))
    return out[:limit]


def _sample_resting_hr(limit: int) -> list[DailyValue]:
    today = date.today()
    vals = [58, 60, 57, 59, 61, 58, 60]
    return [DailyValue(today - timedelta(days=i + 1), float(v), "Sample") for i, v in enumerate(vals)][:limit]
