"""Activity-detail analysis using only fields available on Run."""
from models import Run


def analyze(run: Run, all_runs: list[Run]) -> dict:
    similar = [item for item in all_runs if item.id != run.id and abs(item.distance_km - run.distance_km) <= max(1, run.distance_km * .15)]
    comparison = None
    if similar:
        avg = sum(item.avg_pace_min_km for item in similar) / len(similar)
        delta = round(run.avg_pace_min_km - avg, 2)
        comparison = f"This pace was {abs(delta):.2f} min/km {'slower' if delta > 0 else 'faster'} than {len(similar)} similar-distance run(s)."
    went_well = [f"Completed {run.distance_km} km with {run.elevation_gain_m} m of climbing."]
    if comparison and "faster" in comparison:
        went_well.append("Pace was faster than the available similar-distance baseline.")
    improve = ["Log subjective feedback so future recommendations can account for how this effort felt."]
    if run.avg_hr == 0:
        improve.append("Average heart rate was unavailable, so effort-zone evaluation could not be calculated.")
    return {
        "run": run, "comparison": comparison, "went_well": went_well, "improve": improve,
        "recovery": "Use an easy or rest day next if this effort felt hard, soreness is elevated, or pain is worsening.",
        "unavailable": ["Splits and negative-split detection", "Heart-rate drift", "Cadence changes", "Grade-adjusted pace", "Elevation profile", "Easy-run effort evaluation without personal heart-rate zones"],
    }
