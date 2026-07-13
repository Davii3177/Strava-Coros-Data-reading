"""Small trained model that learns how distance/pace/elevation predict
perceived difficulty from submitted run feedback, and uses that fit to
nudge suggested workout paces toward a target difficulty.

Deliberately kept to a plain linear regression with three coefficients
so the relationship stays inspectable (per this project's "no black-box
AI" stance) rather than swapping in something opaque. `analysis.py` falls
back to its fixed rule-based paces until there's enough feedback to fit
a model that's better than a guess (see MIN_SAMPLES).
"""
from dataclasses import dataclass

from models import Feedback

MIN_SAMPLES = 5


@dataclass
class TrainedWorkoutModel:
    intercept: float
    coef_distance: float
    coef_pace: float
    coef_elevation: float
    sample_count: int

    def predict_difficulty(self, distance_km: float, pace_min_km: float, elevation_gain_m: float) -> float:
        return (
            self.intercept
            + self.coef_distance * distance_km
            + self.coef_pace * pace_min_km
            + self.coef_elevation * elevation_gain_m
        )

    def pace_for_target_difficulty(
        self, target_difficulty: float, distance_km: float, elevation_gain_m: float = 0.0
    ) -> float | None:
        """Solves the fitted line for pace at a fixed distance/elevation.

        Returns None if the model didn't learn the expected relationship
        (slower pace -> lower difficulty, i.e. coef_pace < 0) — inverting it
        in that case would push suggested paces the wrong direction.
        """
        if self.coef_pace >= 0:
            return None
        return (
            target_difficulty
            - self.intercept
            - self.coef_distance * distance_km
            - self.coef_elevation * elevation_gain_m
        ) / self.coef_pace


def train(feedback_entries: list[Feedback]) -> TrainedWorkoutModel | None:
    if len(feedback_entries) < MIN_SAMPLES:
        return None

    from sklearn.linear_model import LinearRegression

    x = [[fb.distance_km, fb.avg_pace_min_km, fb.elevation_gain_m] for fb in feedback_entries]
    y = [fb.difficulty for fb in feedback_entries]

    fitted = LinearRegression().fit(x, y)
    coef_distance, coef_pace, coef_elevation = fitted.coef_
    return TrainedWorkoutModel(
        intercept=fitted.intercept_,
        coef_distance=coef_distance,
        coef_pace=coef_pace,
        coef_elevation=coef_elevation,
        sample_count=len(feedback_entries),
    )
