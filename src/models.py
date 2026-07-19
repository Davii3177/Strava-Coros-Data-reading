from dataclasses import dataclass
from datetime import date, datetime

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
    source: str  # "strava", "coros", or "fitbit"
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
    target_time_min: float | None = None
    priority: bool = False


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
    adherence: str = "not_set"
    dismissed: bool = False


@dataclass
class Shoe:
    id: str
    brand: str
    model: str
    nickname: str
    purchase_date: str
    replacement_km: float | None
    retired: bool = False
    shoe_type: str = "daily"


@dataclass
class SleepNight:
    """A single night's sleep, summarized from stage segments.

    Sourced via the Google Health API (which may aggregate a Fitbit, Coros, or
    other device). Durations are minutes; asleep_min excludes time awake in bed.
    """

    id: str
    date: date  # local calendar day the runner woke up
    start: datetime
    end: datetime
    in_bed_min: float
    asleep_min: float
    deep_min: float
    rem_min: float
    light_min: float
    awake_min: float
    source: str  # friendly device/app label, e.g. "Coros", "Fitbit"

    @property
    def efficiency_pct(self) -> int:
        return round(self.asleep_min / self.in_bed_min * 100) if self.in_bed_min else 0

    @property
    def asleep_str(self) -> str:
        total = round(self.asleep_min)
        return f"{total // 60}h {total % 60:02d}m"


@dataclass
class DailyValue:
    """A once-per-day measurement (e.g. resting heart rate, HRV)."""

    date: date
    value: float
    source: str
