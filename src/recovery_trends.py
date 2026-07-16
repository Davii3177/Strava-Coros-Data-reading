"""Recovery-history summaries without diagnostic claims."""
from collections import defaultdict

from models import RecoveryCheckin


def summarize(checkins: list[RecoveryCheckin]) -> dict:
    by_area = defaultdict(list)
    for item in sorted(checkins, key=lambda entry: entry.created_at):
        for area in item.body_areas:
            by_area[area].append(item.pain_level)
    areas = []
    for area, levels in by_area.items():
        trend = "Stable"
        if len(levels) >= 2:
            trend = "Improving" if levels[-1] < levels[-2] else "Worsening" if levels[-1] > levels[-2] else "Stable"
        areas.append({"area": area.replace("_", " ").title(), "latest": levels[-1], "trend": trend, "entries": len(levels)})
    return {"areas": sorted(areas, key=lambda item: (-item["latest"], item["area"])), "count": len(checkins)}
