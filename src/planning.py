"""Daily workout selection and plan-versus-actual comparison."""
from datetime import date, timedelta

import analysis
from models import Race, Run, format_pace


def todays_run(runs: list[Run], readiness: dict, races: list[Race], today: date | None = None) -> dict:
    today = today or date.today()
    nearest = next((race.date for race in races if race.date >= today), None)
    planned = analysis.weekly_schedule(today, nearest).get(today.weekday(), "Rest")
    avg_pace = analysis.avg_pace_min_km(runs) if runs else 0
    easy_pace = avg_pace + 0.5 if avg_pace else None
    result = {
        "type": planned, "distance_km": None, "duration_min": None, "target": "Easy effort",
        "warmup": "5-10 minutes of easy walking and dynamic mobility.",
        "cooldown": "5-10 minutes easy, then comfortable mobility.",
        "recovery": "At least 24 hours before another hard session.",
        "purpose": "Build consistent aerobic fitness without unnecessary fatigue.",
        "reasons": [f"The weekly schedule assigns {planned.lower()} to {today.strftime('%A')}."]
    }
    if "Tempo" in planned:
        result.update(distance_km=5, duration_min=round(5 * max(avg_pace - .3, 3.0)) if avg_pace else None,
                      target=format_pace(max(avg_pace - .3, 3.0)) if avg_pace else "Controlled comfortably-hard effort",
                      purpose="Develop sustained speed and threshold control.", recovery="Allow 36-48 hours before the next hard session.")
    elif "Easy" in planned:
        result.update(distance_km=5 if "taper" in planned.lower() else 7,
                      duration_min=round((5 if "taper" in planned.lower() else 7) * easy_pace) if easy_pace else None,
                      target=format_pace(easy_pace) if easy_pace else "Conversational effort")
    elif "Long" in planned:
        base = round((sum(run.distance_km for run in runs[:6]) / max(len(runs[:6]), 1)) * 1.6, 1) if runs else 10
        result.update(distance_km=base, duration_min=round(base * easy_pace) if easy_pace else None,
                      target=format_pace(easy_pace) if easy_pace else "Conversational effort",
                      purpose="Build endurance and time-on-feet durability.", recovery="Allow 36-48 hours before a demanding session.")
    elif planned == "Rest":
        result.update(target="Rest or pain-free gentle movement", purpose="Absorb recent training and restore readiness.", recovery="Resume when normal movement feels comfortable.")
    if readiness["tone"] in {"recovery", "reduce"}:
        original = result["type"]
        result.update(type="Recovery day", distance_km=None, duration_min=None,
                      target="Rest or pain-free low-impact movement",
                      purpose="Respond conservatively to current soreness, pain, or training-load signals.",
                      recovery="Reassess symptoms tomorrow before resuming normal training.")
        result["reasons"].append(f"Readiness is '{readiness['status']}', so {original.lower()} was reduced.")
    else:
        result["reasons"].append(f"Readiness is '{readiness['status']}'.")
    return result


def plan_vs_actual(runs: list[Run], races: list[Race], saved: dict, today: date | None = None, feedback_by_run: dict | None = None) -> dict:
    today = today or date.today()
    nearest = next((race.date for race in races if race.date >= today), None)
    runs_by_date = {run.date: run for run in runs}
    schedule = analysis.weekly_schedule(today, nearest)
    start = today - timedelta(days=today.weekday())
    days, missed = [], 0
    for offset in range(7):
        day = start + timedelta(days=offset)
        run = runs_by_date.get(day)
        planned = schedule.get(day.weekday(), "Rest")
        saved_item = saved.get(day.isoformat())
        if run:
            status = "Completed"
        elif saved_item:
            status = saved_item["status"].title()
        elif day < today and planned != "Rest":
            status = "Missed"
            missed += 1
        elif day == today:
            status = "Today"
        else:
            status = "Upcoming"
        days.append({"date": day, "planned": planned, "run": run, "status": status, "saved": saved_item})
    adjustments = []
    if missed:
        adjustments.append(f"{missed} planned session(s) were missed. Continue with the schedule; do not stack missed mileage onto one day.")
    feedback_by_run = feedback_by_run or {}
    hard_dates = sorted({item.date for item in feedback_by_run.values() if item.difficulty >= 4})
    if any((later - earlier).days == 1 for earlier, later in zip(hard_dates, hard_dates[1:])):
        adjustments.append("Consecutive feedback-rated hard days were detected. Keep the next session easy or take recovery time.")
    return {"days": days, "adjustments": adjustments or ["No automatic schedule adjustment is needed from available completion data."]}
