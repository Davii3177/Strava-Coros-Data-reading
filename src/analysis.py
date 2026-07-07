from models import Run


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
    hrs = [r.avg_hr for r in runs]

    if mileage > 0:
        feedback.append(f"Total distance in this set: {mileage} km across {len(runs)} runs.")

    pace_spread = max(paces) - min(paces)
    if pace_spread < 0.3:
        feedback.append(
            "Your pace is very consistent across runs — consider adding a dedicated "
            "easy day or a tempo/interval session to build a wider training stimulus."
        )
    else:
        feedback.append("Good pace variety across easy and harder efforts.")

    if max(hrs) - min(hrs) < 10:
        feedback.append(
            "Heart rate is barely varying between runs — most of your training may be "
            "happening in the same zone. Mixing in true easy (lower HR) days helps recovery."
        )

    long_run = max(runs, key=lambda r: r.distance_km)
    if long_run.distance_km >= 1.5 * (mileage / len(runs)):
        feedback.append(
            f"Your longest run ({long_run.distance_km} km) stands out from the rest — "
            "good long-run structure."
        )

    return feedback


def generate_next_workouts(runs: list[Run]) -> list[str]:
    """Suggests upcoming workouts based on recent load. Rule-based, not AI-generated."""
    if not runs:
        return []

    mileage = weekly_mileage_km(runs)
    avg_pace = avg_pace_min_km(runs)

    easy_pace = round(avg_pace + 0.5, 2)
    tempo_pace = round(avg_pace - 0.3, 2)

    return [
        f"Easy run: 6-8 km @ ~{easy_pace} min/km, keep effort conversational.",
        f"Tempo run: 5 km @ ~{tempo_pace} min/km after a 10 min warm-up.",
        f"Long run: {round(mileage / len(runs) * 1.6, 1)} km @ easy effort, focus on time on feet.",
        "Rest or cross-train: 1-2 days depending on how the above sessions feel.",
    ]
