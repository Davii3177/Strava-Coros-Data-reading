from dataclasses import dataclass
from datetime import date


@dataclass
class Run:
    date: date
    source: str  # "strava" or "coros"
    distance_km: float
    duration_min: float
    avg_hr: int
    avg_pace_min_km: float
    elevation_gain_m: int

    @property
    def pace_str(self) -> str:
        minutes = int(self.avg_pace_min_km)
        seconds = int((self.avg_pace_min_km - minutes) * 60)
        return f"{minutes}:{seconds:02d}/km"
