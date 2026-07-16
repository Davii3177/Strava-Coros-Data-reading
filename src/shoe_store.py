"""Local shoe inventory and activity assignments."""
import json
import os
import secrets
from dataclasses import asdict

from models import Shoe

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PATH = os.path.join(DATA_DIR, "shoes.json")


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


def add(brand: str, model: str, nickname: str, purchase_date: str, replacement_km: float | None) -> Shoe:
    shoe = Shoe(secrets.token_urlsafe(8), brand, model, nickname, purchase_date, replacement_km)
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
