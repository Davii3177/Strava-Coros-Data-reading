"""Local JSON-backed storage for Body & Recovery check-ins."""
import json
import os
from dataclasses import asdict

from models import RecoveryCheckin

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RECOVERY_PATH = os.path.join(DATA_DIR, "recovery_checkins.json")


def load_all() -> list[RecoveryCheckin]:
    if not os.path.exists(RECOVERY_PATH):
        return []
    try:
        with open(RECOVERY_PATH, encoding="utf-8") as file:
            records = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []
    return [RecoveryCheckin(**record) for record in records]


def save(checkin: RecoveryCheckin) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    records = load_all()
    records.insert(0, checkin)
    with open(RECOVERY_PATH, "w", encoding="utf-8") as file:
        json.dump([asdict(record) for record in records], file, indent=2)
