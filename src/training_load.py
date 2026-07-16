"""Transparent training-load and readiness calculations."""
from datetime import date, timedelta

from models import Feedback, RecoveryCheckin, Run


def calculate(
    runs: list[Run],
    feedback_by_run: dict[str, Feedback],
    checkins: list[RecoveryCheckin],
    today: date | None = None,
) -> dict:
    today = today or date.today()
    recent_start = today - timedelta(days=6)
    prior_start = today - timedelta(days=34)
    recent = [run for run in runs if recent_start <= run.date <= today]
    prior = [run for run in runs if prior_start <= run.date < recent_start]
    recent_km = round(sum(run.distance_km for run in recent), 1)
    prior_km = round(sum(run.distance_km for run in prior), 1)
    prior_weekly = round(prior_km / 4, 1)
    change = round((recent_km - prior_weekly) / prior_weekly * 100, 1) if prior_weekly else None
    recent_feedback = [feedback_by_run[run.id] for run in recent if run.id in feedback_by_run]
    soreness = round(sum(item.soreness for item in recent_feedback) / len(recent_feedback), 1) if recent_feedback else None
    motivation = round(sum(item.motivation for item in recent_feedback) / len(recent_feedback), 1) if recent_feedback else None
    recent_checkins = [item for item in checkins if item.created_at[:10] >= recent_start.isoformat()]
    peak_pain = max((item.pain_level for item in recent_checkins), default=None)
    urgent = any(item.urgent for item in recent_checkins)
    recent_elevation = sum(run.elevation_gain_m for run in recent)
    hard_sessions = sum(1 for item in recent_feedback if item.difficulty >= 4)

    reasons = [f"{recent_km} km in the last 7 days versus a {prior_weekly} km prior weekly average."]
    status = "Ready to train"
    tone = "ready"
    if urgent or (peak_pain is not None and peak_pain >= 8):
        status, tone = "Recovery recommended", "recovery"
        reasons.append("A recent recovery check-in contains severe or urgent symptoms.")
    elif soreness is not None and soreness >= 4:
        status, tone = "Reduce load", "reduce"
        reasons.append(f"Average logged soreness is {soreness}/5.")
    elif change is not None and change > 40:
        status, tone = "Reduce load", "reduce"
        reasons.append(f"Distance is {change:.0f}% above the previous four-week weekly average.")
    elif change is not None and change > 15:
        status, tone = "Maintain current load", "maintain"
        reasons.append(f"Distance has increased {change:.0f}%; avoid adding another large jump.")
    else:
        reasons.append("No high soreness, severe pain, or large load spike is present in available data.")
    if soreness is None:
        reasons.append("Soreness is unavailable until run feedback is logged.")
    if motivation is not None:
        reasons.append(f"Average motivation is {motivation}/5.")
    reasons.append(f"Available activities include {recent_elevation} m of climbing and {hard_sessions} feedback-rated hard session(s).")
    return {
        "status": status, "tone": tone, "reasons": reasons,
        "recent_km": recent_km, "prior_weekly_km": prior_weekly,
        "change_percent": change, "soreness": soreness, "motivation": motivation,
        "peak_pain": peak_pain, "recent_elevation_m": recent_elevation, "hard_sessions": hard_sessions,
        "missing": [name for name, value in (("sleep", None), ("HRV", None), ("resting heart rate", None)) if value is None],
    }
