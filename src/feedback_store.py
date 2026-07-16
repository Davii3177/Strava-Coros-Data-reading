"""Local JSON-backed storage for per-run feedback (difficulty/soreness/motivation)."""
import json
import os
from dataclasses import asdict
from datetime import date

from models import Feedback

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.json")
DISMISSED_PATH = os.path.join(DATA_DIR, "feedback_dismissed.json")


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

    dismissed = load_dismissed()
    if feedback.run_id in dismissed:
        dismissed.remove(feedback.run_id)
        _save_dismissed(dismissed)


def delete(run_id: str) -> bool:
    """Delete one saved feedback entry without touching the source activity."""
    all_feedback = load_all()
    if run_id not in all_feedback:
        return False

    del all_feedback[run_id]
    os.makedirs(DATA_DIR, exist_ok=True)
    serializable = {
        item_id: {**asdict(fb), "date": fb.date.isoformat()}
        for item_id, fb in all_feedback.items()
    }
    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    return True


def load_dismissed() -> set[str]:
    if not os.path.exists(DISMISSED_PATH):
        return set()
    with open(DISMISSED_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return {str(run_id) for run_id in raw if run_id}


def dismiss(run_id: str) -> None:
    dismissed = load_dismissed()
    dismissed.add(run_id)
    _save_dismissed(dismissed)


def _save_dismissed(run_ids: set[str]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DISMISSED_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(run_ids), f, indent=2)
