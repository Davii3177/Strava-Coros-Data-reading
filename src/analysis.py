from datetime import date, timedelta

from models import Run, format_pace
from workout_model import MIN_SAMPLES, TrainedWorkoutModel

TAPER_WINDOW_DAYS = 10
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Weekday index (Monday=0 .. Sunday=6) -> workout label. This is the single
# source of truth for both the calendar view and "Suggested next workouts",
# so the two always agree on what day X's session is.
BASE_WEEKLY_SCHEDULE = {
    0: "Easy run",
    1: "Tempo run",
    2: "Easy run",
    3: "Easy run",
    4: "Tempo run",
    5: "Long run",
    6: "Rest",
}
TAPER_WEEKLY_SCHEDULE = {
    0: "Easy run (taper)",
    1: "Easy run (taper)",
    2: "Easy run (taper)",
    3: "Easy run (taper)",
    4: "Easy run (taper)",
    5: "Easy run (taper)",
    6: "Rest",
}


def days_to_race(today: date, nearest_race_date: date | None) -> int | None:
    return (nearest_race_date - today).days if nearest_race_date else None


def is_tapering(today: date, nearest_race_date: date | None) -> bool:
    days = days_to_race(today, nearest_race_date)
    return days is not None and 0 <= days <= TAPER_WINDOW_DAYS


def weekly_schedule(today: date, nearest_race_date: date | None = None) -> dict[int, str]:
    """Maps weekday -> workout label. Automatically tapers to easy/rest-only
    in the window before a set race day."""
    return TAPER_WEEKLY_SCHEDULE if is_tapering(today, nearest_race_date) else BASE_WEEKLY_SCHEDULE


def weekly_mileage_km(runs: list[Run]) -> float:
    return round(sum(r.distance_km for r in runs), 1)


def avg_pace_min_km(runs: list[Run]) -> float:
    if not runs:
        return 0.0
    return round(sum(r.avg_pace_min_km for r in runs) / len(runs), 2)


def generate_feedback(runs: list[Run]) -> list[str]:
    """Rule-based feedback on recent training. No LLM involved."""
    if not runs:
        return ["No runs found yet. Connect Strava or Coros to get feedback."]

    feedback = []
    mileage = weekly_mileage_km(runs)
    paces = [r.avg_pace_min_km for r in runs]
    hrs = [r.avg_hr for r in runs if r.avg_hr > 0]

    if mileage > 0:
        feedback.append(f"Across the {len(runs)} loaded runs, you covered {mileage} km.")

    pace_spread = max(paces) - min(paces)
    if pace_spread < 0.3:
        feedback.append(
            f"Pace varied by only {pace_spread:.2f} min/km across the loaded runs. "
            "If these were meant to serve different purposes, make easy days easier before adding more intensity."
        )
    else:
        feedback.append(f"Pace spans {pace_spread:.2f} min/km across the loaded runs, showing a mix of effort levels.")

    if len(hrs) >= 2 and max(hrs) - min(hrs) < 10:
        feedback.append(
            f"Average heart rate varies by {max(hrs) - min(hrs)} bpm across runs with heart-rate data. "
            "That may mean several sessions landed at a similar effort, so keep recovery runs clearly easy."
        )

    long_run = max(runs, key=lambda r: r.distance_km)
    if long_run.distance_km >= 1.5 * (mileage / len(runs)):
        feedback.append(
            f"Your longest run was {long_run.distance_km} km, at least 50% longer than the average loaded run."
        )

    return feedback


def generate_next_workouts(
    runs: list[Run],
    model: TrainedWorkoutModel | None = None,
    nearest_race_date: date | None = None,
) -> list[str]:
    """Day-by-day forecast for the next 7 days, built from the same
    weekly_schedule() the calendar view renders — so a given date always shows
    the same workout type in both places.

    Baseline paces are a fixed rule-based offset from your recent average.
    If a trained model (see workout_model.py) is passed in, its fitted
    distance/pace/elevation -> difficulty relationship is used instead, aimed
    at a target difficulty per workout type — so easy/tempo paces adapt as
    you log more feedback, without becoming an opaque black box.

    If a race is set within TAPER_WINDOW_DAYS, long-run volume is cut and the
    schedule switches to TAPER_WEEKLY_SCHEDULE — same rule the calendar uses.
    """
    if not runs:
        return []

    mileage = weekly_mileage_km(runs)
    avg_pace = avg_pace_min_km(runs)
    long_run_km = round(mileage / len(runs) * 1.6, 1)

    today = date.today()
    tapering = is_tapering(today, nearest_race_date)
    if tapering:
        long_run_km = round(long_run_km * 0.6, 1)

    easy_pace = round(avg_pace + 0.5, 2)
    tempo_pace = round(avg_pace - 0.3, 2)

    model_note = None
    if model:
        adjusted_easy = model.pace_for_target_difficulty(target_difficulty=2.0, distance_km=7.0)
        adjusted_tempo = model.pace_for_target_difficulty(target_difficulty=4.0, distance_km=5.0)
        if adjusted_easy is not None and adjusted_tempo is not None and adjusted_easy > adjusted_tempo > 0:
            easy_pace = round(adjusted_easy, 2)
            tempo_pace = round(adjusted_tempo, 2)
            model_note = (
                f"Pace targets above adjusted using a trained model fit on "
                f"{model.sample_count} logged feedback entries."
            )
        else:
            model_note = (
                f"{model.sample_count} feedback entries logged, but the trained model's "
                "pace/difficulty relationship isn't reliable yet — using rule-based baseline paces."
            )

    workout_descriptions = {
        "Easy run": f"Easy run: 6-8 km @ ~{format_pace(easy_pace)}, keep effort conversational.",
        "Tempo run": f"Tempo run: 5 km @ ~{format_pace(tempo_pace)} after a 10 min warm-up.",
        "Long run": f"Long run: {long_run_km} km @ easy effort, focus on time on feet.",
        "Easy run (taper)": f"Easy run: 4-6 km @ ~{format_pace(easy_pace)}, keep it light.",
        "Rest": "Rest or light cross-train.",
    }

    schedule = weekly_schedule(today, nearest_race_date)
    run_dates = {r.date for r in runs}

    workouts = []
    if tapering:
        days = days_to_race(today, nearest_race_date)
        workouts.append(
            f"Race day in {days} day(s) — tapering this week: reduced long-run "
            "volume, easy effort only, extra rest."
        )

    for offset in range(7):
        day = today + timedelta(days=offset)
        label = "Today" if offset == 0 else "Tomorrow" if offset == 1 else WEEKDAY_NAMES[day.weekday()]
        day_str = day.strftime("%a %b %d")
        if day == nearest_race_date:
            workouts.append(f"{label} ({day_str}): Race day — good luck!")
        elif day in run_dates:
            workouts.append(f"{label} ({day_str}): already logged.")
        else:
            plan = schedule.get(day.weekday(), "Rest")
            workouts.append(f"{label} ({day_str}): {workout_descriptions.get(plan, plan)}")

    workouts.append(
        model_note
        or f"Pace targets are the rule-based baseline — log feedback on {MIN_SAMPLES}+ runs "
        "to unlock model-based adjustment."
    )
    return workouts
