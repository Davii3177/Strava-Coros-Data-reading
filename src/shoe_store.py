"""Local shoe inventory and activity assignments."""
import json
import os
import secrets
from dataclasses import asdict

from models import Shoe

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PATH = os.path.join(DATA_DIR, "shoes.json")
SHOE_TYPES = {"race", "tempo", "workout", "daily", "recovery"}


def _raw() -> dict:
    if not os.path.exists(PATH):
        return {"shoes": [], "assignments": {}}
    try:
        with open(PATH, encoding="utf-8") as file:
            raw = json.load(file)
        raw.setdefault("shoes", [])
        raw.setdefault("assignments", {})
        return raw
    except (OSError, json.JSONDecodeError):
        return {"shoes": [], "assignments": {}}


def _write(raw: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as file:
        json.dump(raw, file, indent=2)


def load_all() -> list[Shoe]:
    return [Shoe(**item) for item in _raw()["shoes"]]


def assignments() -> dict[str, str]:
    return _raw()["assignments"]


def add(brand: str, model: str, nickname: str, purchase_date: str, replacement_km: float | None, shoe_type: str = "daily") -> Shoe:
    if shoe_type not in SHOE_TYPES:
        raise ValueError("Invalid shoe type")
    shoe = Shoe(secrets.token_urlsafe(8), brand, model, nickname, purchase_date, replacement_km, shoe_type=shoe_type)
    raw = _raw()
    raw["shoes"].append(asdict(shoe))
    _write(raw)
    return shoe


def retire(shoe_id: str) -> bool:
    raw = _raw()
    for shoe in raw["shoes"]:
        if shoe["id"] == shoe_id:
            shoe["retired"] = True
            _write(raw)
            return True
    return False


def set_type(shoe_id: str, shoe_type: str) -> bool:
    if shoe_type not in SHOE_TYPES:
        return False
    raw = _raw()
    for shoe in raw["shoes"]:
        if shoe["id"] == shoe_id:
            shoe["shoe_type"] = shoe_type
            _write(raw)
            return True
    return False


def assign(run_id: str, shoe_id: str) -> None:
    raw = _raw()
    raw["assignments"][run_id] = shoe_id
    _write(raw)


def with_mileage(runs, feedback_by_run=None) -> list[dict]:
    feedback_by_run = feedback_by_run or {}
    assigned = assignments()
    totals = {shoe.id: 0.0 for shoe in load_all()}
    shoe_runs = {shoe.id: [] for shoe in load_all()}
    for run in runs:
        if assigned.get(run.id) in totals:
            totals[assigned[run.id]] += run.distance_km
            shoe_runs[assigned[run.id]].append(run)
    result = []
    for shoe in load_all():
        mileage = round(totals[shoe.id], 1)
        percent = round(mileage / shoe.replacement_km * 100) if shoe.replacement_km else None
        assigned_runs = shoe_runs[shoe.id]
        average_pace = round(sum(run.avg_pace_min_km for run in assigned_runs) / len(assigned_runs), 2) if assigned_runs else None
        soreness_values = [feedback_by_run[run.id].soreness for run in assigned_runs if run.id in feedback_by_run]
        average_soreness = round(sum(soreness_values) / len(soreness_values), 1) if soreness_values else None
        result.append({"shoe": shoe, "mileage_km": mileage, "replacement_percent": percent, "average_pace": average_pace, "average_soreness": average_soreness})
    return result


def suggest_for_today(runs, feedback_by_run=None, workout_type: str = "") -> dict | None:
    """Choose a conservative daily shoe from the active rotation.

    The recommendation favors shoes with lower runner-reported soreness and
    less replacement wear. It is a rotation aid, not evidence that one shoe
    caused or prevented discomfort.
    """
    candidates = [item for item in with_mileage(runs, feedback_by_run) if not item["shoe"].retired]
    if not candidates:
        return None

    usable = [item for item in candidates if item["replacement_percent"] is None or item["replacement_percent"] < 100]
    candidates = usable or candidates

    normalized_workout = workout_type.lower()
    desired_type = (
        "race" if "race" in normalized_workout else
        "tempo" if "tempo" in normalized_workout else
        "workout" if any(word in normalized_workout for word in ("interval", "speed", "workout")) else
        "recovery" if "recovery" in normalized_workout else
        "daily"
    )
    purpose_matches = [item for item in candidates if item["shoe"].shoe_type == desired_type]
    if purpose_matches:
        candidates = purpose_matches

    def rank(item):
        soreness = item["average_soreness"] if item["average_soreness"] is not None else 3.0
        replacement = item["replacement_percent"] if item["replacement_percent"] is not None else 0
        return (soreness, replacement, item["mileage_km"])

    chosen = min(candidates, key=rank)
    purpose_prefix = f"Matched to today’s {desired_type} session. " if purpose_matches else "No exact purpose match; "
    if chosen["average_soreness"] is not None:
        reason = purpose_prefix + f"Lowest logged soreness in the eligible rotation ({chosen['average_soreness']}/5)."
    elif chosen["replacement_percent"] is not None:
        reason = purpose_prefix + f"only {chosen['replacement_percent']}% of its replacement distance is assigned."
    else:
        reason = purpose_prefix + "least assigned mileage among eligible shoes."
    return {**chosen, "reason": reason, "desired_type": desired_type, "purpose_matched": bool(purpose_matches)}
