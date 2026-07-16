"""Personal records derived only from available activity summaries."""
from collections import defaultdict

from models import Run


DISTANCES = [(1.0, "Fastest 1K"), (1.609, "Fastest mile"), (5.0, "Fastest 5K"), (10.0, "Fastest 10K"), (21.0975, "Fastest half marathon"), (42.195, "Fastest marathon")]


def calculate(runs: list[Run]) -> dict:
    if not runs:
        return {"records": [], "unavailable": ["No activity data is available."]}
    records = [
        {"label": "Longest run", "value": f"{max(runs, key=lambda run: run.distance_km).distance_km} km", "kind": "Calculated"},
        {"label": "Greatest elevation gain", "value": f"{max(run.elevation_gain_m for run in runs)} m", "kind": "Calculated"},
    ]
    weeks = defaultdict(float)
    for run in runs:
        iso = run.date.isocalendar()
        weeks[(iso.year, iso.week)] += run.distance_km
    records.append({"label": "Highest-mileage week", "value": f"{max(weeks.values()):.1f} km", "kind": "Calculated"})
    ordered_weeks = sorted(weeks)
    longest, current = 1, 1
    for previous, current_week in zip(ordered_weeks, ordered_weeks[1:]):
        consecutive = (current_week[0] == previous[0] and current_week[1] == previous[1] + 1) or (current_week[0] == previous[0] + 1 and previous[1] >= 52 and current_week[1] == 1)
        current = current + 1 if consecutive else 1
        longest = max(longest, current)
    records.append({"label": "Consistency streak", "value": f"{longest} week{'s' if longest != 1 else ''}", "kind": "Calculated from weeks with a run"})
    for distance, label in DISTANCES:
        matches = [run for run in runs if abs(run.distance_km - distance) / distance <= .05]
        if matches:
            best = min(matches, key=lambda run: run.duration_min)
            records.append({"label": label, "value": f"{best.duration_min:.1f} min", "kind": "Estimated from activity"})
    return {"records": records, "unavailable": ["Strongest negative split requires split data from the activity source.", "Official race records require an official-result field."]}
