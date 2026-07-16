from dataclasses import dataclass
from datetime import date

KM_TO_MILES = 0.621371


def format_pace(pace_min_km: float) -> str:
    """Formats a decimal min/km pace as e.g. '4:55/km (7.6 mph)'."""
    minutes = int(pace_min_km)
    seconds = round((pace_min_km - minutes) * 60)
    if seconds == 60:
        minutes += 1
        seconds = 0
    mph = (60 / pace_min_km) * KM_TO_MILES if pace_min_km else 0.0
    return f"{minutes}:{seconds:02d}/km ({mph:.1f} mph)"


@dataclass
class Run:
    id: str
    date: date
    source: str  # "strava" or "coros"
    distance_km: float
    duration_min: float
    avg_hr: int
    avg_pace_min_km: float
    elevation_gain_m: int

    @property
    def pace_str(self) -> str:
        return format_pace(self.avg_pace_min_km)


@dataclass
class Feedback:
    """Subjective feedback logged for a specific run.

    Run metrics are captured at submission time (rather than referencing the
    Run object) so the model can keep training on past feedback even after a
    run ages out of the API's "recent activities" window.
    """

    run_id: str
    date: date
    distance_km: float
    avg_pace_min_km: float
    elevation_gain_m: int
    difficulty: int  # 1 (very easy) - 5 (very hard)
    soreness: int  # 1 (none) - 5 (severe)
    motivation: int  # 1 (very low) - 5 (very high)
    comment: str
    submitted_at: str  # ISO timestamp


@dataclass
class Race:
    date: date
    name: str
    distance_km: float | None = None


@dataclass
class RecoveryCheckin:
    """A body-pain check-in retained locally alongside workout feedback."""

    id: str
    body_areas: list[str]
    pain_level: int
    onset: str
    sensation: list[str]
    triggers: list[str]
    notes: str
    training_context: dict
    guidance: str
    urgent: bool
    created_at: str
    side: str = "both"
    location_detail: str = ""
