"""Local JSON-backed storage for race days."""
import json
import os
from dataclasses import asdict
from datetime import date

from models import Race

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RACES_PATH = os.path.join(DATA_DIR, "races.json")


def _load_raw() -> dict:
    if not os.path.exists(RACES_PATH):
        return {}
    with open(RACES_PATH, encoding="utf-8") as f:
        return json.load(f)


def _write_raw(raw: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RACES_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)


def load_all() -> list[Race]:
    races = [
        Race(
            date=date.fromisoformat(entry["date"]),
            name=entry["name"],
            distance_km=entry.get("distance_km"),
            target_time_min=entry.get("target_time_min"),
            priority=entry.get("priority", False),
        )
        for entry in _load_raw().values()
    ]
    races.sort(key=lambda r: r.date)
    return races


def save(race: Race) -> None:
    raw = _load_raw()
    raw[race.date.isoformat()] = {**asdict(race), "date": race.date.isoformat()}
    _write_raw(raw)


def delete(date_str: str) -> None:
    raw = _load_raw()
    raw.pop(date_str, None)
    _write_raw(raw)
