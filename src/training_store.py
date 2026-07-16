"""JSON persistence for planned-workout outcomes."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PATH = os.path.join(DATA_DIR, "training_plan.json")


def load_all() -> dict:
    if not os.path.exists(PATH):
        return {}
    try:
        with open(PATH, encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


def save(day: str, status: str, actual_distance_km: float | None, note: str) -> None:
    records = load_all()
    records[day] = {"status": status, "actual_distance_km": actual_distance_km, "note": note[:300]}
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
