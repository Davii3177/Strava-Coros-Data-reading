"""Explainable race-phase and finish-range estimates."""
from datetime import date

from models import Race, Run, format_pace


def goal_center(races: list[Race], runs: list[Run], today: date | None = None) -> dict | None:
    today = today or date.today()
    future = [race for race in races if race.date >= today]
    race = next((item for item in future if item.priority), future[0] if future else None)
    if not race:
        return None
    days = (race.date - today).days
    phase = "Race" if days == 0 else "Taper" if days <= 10 else "Peak" if days <= 28 else "Build" if days <= 84 else "Base"
    target_pace = race.target_time_min / race.distance_km if race.target_time_min and race.distance_km else None
    prediction = None
    if race.distance_km and runs:
        candidates = [run for run in runs if run.distance_km > 0 and run.duration_min > 0]
        if candidates:
            best = min(candidates, key=lambda run: run.duration_min * (race.distance_km / run.distance_km) ** 1.06)
            estimate = best.duration_min * (race.distance_km / best.distance_km) ** 1.06
            confidence = "Moderate" if len(candidates) >= 5 and .5 <= best.distance_km / race.distance_km <= 1.5 else "Low"
            prediction = {
                "low_min": round(estimate * .95), "high_min": round(estimate * 1.05), "confidence": confidence,
                "explanation": f"Riegel estimate from a {best.distance_km} km run in {best.duration_min:.0f} minutes; range is +/-5% and is not guaranteed."
            }
    checklist = ["Confirm shoes and race logistics", "Prioritize sleep and familiar meals", "Avoid unplanned hard efforts"] if days <= 10 else ["Follow the current phase consistently", "Practice fueling on longer runs", "Log feedback after key sessions"]
    pacing = "Start controlled, settle near goal effort, and only increase effort late if the pace remains sustainable." if target_pace else "Set a target time to generate a target pace; begin conservatively and avoid an early surge."
    return {"race": race, "days": days, "phase": phase, "target_pace": format_pace(target_pace) if target_pace else None, "prediction": prediction, "checklist": checklist, "pacing": pacing}
