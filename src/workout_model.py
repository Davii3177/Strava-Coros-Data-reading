"""Small trained model that learns how distance/pace/elevation predict
perceived difficulty from submitted run feedback, and uses that fit to
nudge suggested workout paces toward a target difficulty.

Deliberately a plain linear regression with three coefficients so the
relationship stays inspectable (per this project's "no black-box AI" stance).
The fit is ordinary least squares solved in pure Python (normal equations +
Gaussian elimination) so there is no heavy native dependency — this keeps the
app portable to constrained runtimes (e.g. Cloudflare Workers / Pyodide) where
scikit-learn/scipy cannot be bundled. `analysis.py` falls back to its fixed
rule-based paces until there's enough feedback to fit a model (see MIN_SAMPLES),
and `train` returns None if the feedback is degenerate (e.g. collinear inputs),
so the caller safely stays on the rules.
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


def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    """Solve `matrix @ x = vector` via Gaussian elimination with partial
    pivoting. Returns None if the system is singular (no unique solution)."""
    size = len(vector)
    # Work on an augmented copy so the inputs are left untouched.
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(augmented[r][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        for r in range(size):
            if r == col:
                continue
            factor = augmented[r][col] / pivot_value
            if factor:
                for c in range(col, size + 1):
                    augmented[r][c] -= factor * augmented[col][c]
    return [augmented[i][size] / augmented[i][i] for i in range(size)]


def _fit_ols(rows: list[list[float]], targets: list[float]) -> list[float] | None:
    """Ordinary least squares with an intercept term, via the normal equations
    (X^T X) b = X^T y. `rows` are the feature vectors; returns
    [intercept, *coefficients] or None when the fit is not well-determined."""
    design = [[1.0, *row] for row in rows]  # prepend the intercept column
    width = len(design[0])
    gram = [[0.0] * width for _ in range(width)]
    moment = [0.0] * width
    for features, target in zip(design, targets):
        for i in range(width):
            moment[i] += features[i] * target
            for j in range(width):
                gram[i][j] += features[i] * features[j]
    return _solve_linear_system(gram, moment)


def train(feedback_entries: list[Feedback]) -> TrainedWorkoutModel | None:
    if len(feedback_entries) < MIN_SAMPLES:
        return None

    rows = [[fb.distance_km, fb.avg_pace_min_km, fb.elevation_gain_m] for fb in feedback_entries]
    targets = [fb.difficulty for fb in feedback_entries]

    solution = _fit_ols(rows, targets)
    if solution is None:
        return None

    intercept, coef_distance, coef_pace, coef_elevation = solution
    return TrainedWorkoutModel(
        intercept=intercept,
        coef_distance=coef_distance,
        coef_pace=coef_pace,
        coef_elevation=coef_elevation,
        sample_count=len(feedback_entries),
    )
