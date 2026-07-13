"""Local JSON-backed storage for per-run feedback (difficulty/soreness/motivation)."""
import json
import os
from dataclasses import asdict
from datetime import date

from models import Feedback

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.json")


def load_all() -> dict[str, Feedback]:
    if not os.path.exists(FEEDBACK_PATH):
        return {}

    with open(FEEDBACK_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    return {
        run_id: Feedback(**{**entry, "date": date.fromisoformat(entry["date"])})
        for run_id, entry in raw.items()
    }


def save(feedback: Feedback) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    all_feedback = load_all()
    all_feedback[feedback.run_id] = feedback

    serializable = {
        run_id: {**asdict(fb), "date": fb.date.isoformat()}
        for run_id, fb in all_feedback.items()
    }
    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
