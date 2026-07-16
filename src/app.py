import calendar as pycalendar
import hmac
import json
import os
import secrets
from datetime import date, datetime, timedelta, timezone

import plotly.graph_objects as go
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, redirect, render_template, request, session, url_for

import analysis
import coros_client
import feedback_store
import personal_records
import planning
import race_store
import race_prediction
import recovery_store
import recovery_trends
import run_analysis
import shoe_store
import strava_client
import training_load
import training_store
import workout_model
from models import Feedback, Race, RecoveryCheckin, Run, format_pace

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


def _password_ok(entered: str) -> bool:
    expected = os.environ.get("APP_PASSWORD")
    return bool(expected) and hmac.compare_digest(entered, expected)


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("authenticated"):
        error = None
        if request.method == "POST":
            if not os.environ.get("APP_PASSWORD"):
                error = "APP_PASSWORD is not set in .env. Refusing to start."
            elif _password_ok(request.form.get("password", "")):
                session["authenticated"] = True
                return redirect(url_for("index"))
            else:
                error = "Incorrect password."
        return render_template("login.html", error=error)

    return render_template("dashboard.html", **_dashboard_context())


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("index"))


@app.route("/feedback/<run_id>", methods=["POST"])
def submit_feedback(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))

    run = next((r for r in _all_runs() if r.id == run_id), None)
    if run is None:
        abort(404)

    try:
        difficulty = int(request.form["difficulty"])
        soreness = int(request.form["soreness"])
        motivation = int(request.form["motivation"])
    except (KeyError, ValueError):
        abort(400)
    if not all(1 <= value <= 5 for value in (difficulty, soreness, motivation)):
        abort(400)

    feedback_store.save(
        Feedback(
            run_id=run.id,
            date=run.date,
            distance_km=run.distance_km,
            avg_pace_min_km=run.avg_pace_min_km,
            elevation_gain_m=run.elevation_gain_m,
            difficulty=difficulty,
            soreness=soreness,
            motivation=motivation,
            comment=request.form.get("comment", "").strip(),
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    return redirect(url_for("index") + "#feedback")


@app.route("/feedback/<run_id>/delete", methods=["POST"])
def delete_feedback(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    feedback_store.delete(run_id)
    return redirect(url_for("index") + "#feedback")


@app.route("/feedback/<run_id>/dismiss", methods=["POST"])
def dismiss_feedback(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))

    run = next((item for item in _all_runs() if item.id == run_id), None)
    if run is None:
        abort(404)
    if run_id not in feedback_store.load_all():
        feedback_store.dismiss(run_id)
    return redirect(url_for("index") + "#feedback")


@app.route("/races", methods=["POST"])
def add_race():
    if not session.get("authenticated"):
        return redirect(url_for("index"))

    try:
        race_date = date.fromisoformat(request.form["date"])
    except (KeyError, ValueError):
        abort(400)

    name = request.form.get("name", "").strip()
    if not name:
        abort(400)

    distance_raw = request.form.get("distance_km", "").strip()
    try:
        distance_km = float(distance_raw) if distance_raw else None
    except ValueError:
        abort(400)
    if distance_km is not None and not 0 < distance_km <= 500:
        abort(400)

    target_raw = request.form.get("target_time_min", "").strip()
    try:
        target_time_min = float(target_raw) if target_raw else None
    except ValueError:
        abort(400)
    if target_time_min is not None and not 0 < target_time_min <= 10000:
        abort(400)
    priority = request.form.get("priority") == "on"

    race_store.save(Race(date=race_date, name=name, distance_km=distance_km, target_time_min=target_time_min, priority=priority))
    return redirect(url_for("index"))


@app.route("/races/<date_str>/delete", methods=["POST"])
def delete_race(date_str):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    race_store.delete(date_str)
    return redirect(url_for("index"))


@app.route("/training/today", methods=["POST"])
def update_today_status():
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    status = request.form.get("status", "")
    if status not in {"complete", "skipped", "shortened", "modified"}:
        abort(400)
    distance_raw = request.form.get("actual_distance_km", "").strip()
    try:
        distance_km = float(distance_raw) if distance_raw else None
    except ValueError:
        abort(400)
    if distance_km is not None and not 0 <= distance_km <= 500:
        abort(400)
    training_store.save(date.today().isoformat(), status, distance_km, request.form.get("note", "").strip())
    return redirect(url_for("index") + "#daily")


@app.route("/shoes", methods=["POST"])
def add_shoe():
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    brand = request.form.get("brand", "").strip()
    model = request.form.get("model", "").strip()
    nickname = request.form.get("nickname", "").strip()
    purchase_date = request.form.get("purchase_date", "").strip()
    if not brand or not model or len(brand) > 80 or len(model) > 80 or len(nickname) > 80:
        abort(400)
    if purchase_date:
        try:
            date.fromisoformat(purchase_date)
        except ValueError:
            abort(400)
    replacement_raw = request.form.get("replacement_km", "").strip()
    try:
        replacement_km = float(replacement_raw) if replacement_raw else None
    except ValueError:
        abort(400)
    if replacement_km is not None and not 1 <= replacement_km <= 5000:
        abort(400)
    shoe_store.add(brand, model, nickname, purchase_date, replacement_km)
    return redirect(url_for("index") + "#shoes")


@app.route("/shoes/<shoe_id>/retire", methods=["POST"])
def retire_shoe(shoe_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    if not shoe_store.retire(shoe_id):
        abort(404)
    return redirect(url_for("index") + "#shoes")


@app.route("/runs/<run_id>/shoe", methods=["POST"])
def assign_run_shoe(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    if not any(run.id == run_id for run in _all_runs()):
        abort(404)
    shoe_id = request.form.get("shoe_id", "")
    if shoe_id not in {shoe.id for shoe in shoe_store.load_all()}:
        abort(400)
    shoe_store.assign(run_id, shoe_id)
    return redirect(url_for("index") + "#shoes")


@app.route("/runs/<run_id>")
def run_detail(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    runs = _all_runs()
    run = next((item for item in runs if item.id == run_id), None)
    if not run:
        abort(404)
    return render_template("run_detail.html", analysis=run_analysis.analyze(run, runs))


@app.route("/recovery/<checkin_id>/adherence", methods=["POST"])
def recovery_adherence(checkin_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    adherence = request.form.get("adherence", "")
    if adherence not in {"followed", "partial", "not_followed"}:
        abort(400)
    if not recovery_store.update_adherence(checkin_id, adherence):
        abort(404)
    return redirect(url_for("index") + "#recovery-timeline")


@app.route("/recovery/export")
def export_recovery():
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    lines = ["Gaman AI recovery check-in summary", "Educational history only; not a diagnosis or treatment record.", ""]
    for item in recovery_store.load_all():
        lines.append(f"{item.created_at[:10]} | {', '.join(item.body_areas)} | {item.side} | pain {item.pain_level}/10 | trend action: {item.adherence}")
        if item.location_detail:
            lines.append(f"Exact location: {item.location_detail}")
        lines.append(f"Notes: {item.notes or 'None'}")
        lines.append("")
    return Response("\n".join(lines), mimetype="text/plain", headers={"Content-Disposition": "attachment; filename=gaman-recovery-summary.txt"})


def _all_runs() -> list[Run]:
    strava_configured = strava_client.is_configured()
    coros_configured = coros_client.is_configured()
    if not strava_configured and not coros_configured:
        runs = strava_client.fetch_runs(limit=50) + coros_client.fetch_runs(limit=50)
    else:
        runs = strava_client.fetch_runs(limit=50) if strava_configured else []
        if coros_configured:
            try:
                runs += coros_client.fetch_runs(limit=50)
            except NotImplementedError:
                pass
    runs.sort(key=lambda r: r.date, reverse=True)
    return runs


# Validated (CVD-safe, contrast-checked on both the light and dark surfaces
# in style.css) categorical colors, one per data source. Kept separate from
# the UI accent color so chart identity never gets confused with brand chrome.
SOURCE_COLORS = {"strava": "#3987e5", "coros": "#d95926"}

BODY_AREAS = {
    "head_face", "jaw", "neck", "collarbones", "shoulders", "biceps_triceps",
    "elbows", "forearms", "wrists_hands", "chest", "ribs", "abdomen",
    "upper_back", "mid_back", "lower_back", "sacrum_si", "hips", "hip_flexors",
    "glutes", "groin_adductors", "quads", "inner_thighs", "outer_thighs",
    "hamstrings", "kneecap", "inner_knee", "outer_knee", "shins", "calves",
    "achilles", "ankles", "heels", "feet", "toes",
    # Accept broad-region values from existing cached versions of the UI.
    "shoulders", "upper_back", "lower_back", "chest", "elbows", "wrists_hands",
    "hips", "glutes", "groin", "quads", "hamstrings", "knees", "shins", "calves",
    "ankles", "feet",
}
SENSATIONS = {"sharp", "dull", "tight", "sore", "burning", "numb", "tingling"}
TRIGGERS = {"running", "walking", "rest", "movement"}
ONSET_OPTIONS = {"gradual", "sudden", "after_run"}
BODY_SIDES = {"left", "right", "both", "center"}
RED_FLAG_TERMS = {
    "unable to bear weight", "cannot bear weight", "deformity", "chest pain",
    "trouble breathing", "shortness of breath", "fever", "numbness", "weakness",
    "bladder", "bowel", "trauma", "traumatic swelling",
}
AI_RATE_LIMIT = 5
AI_RATE_WINDOW_SECONDS = 3600


def _training_context(runs: list[Run]) -> dict:
    recent = runs[:7]
    prior = runs[7:14]
    recent_distance = round(sum(run.distance_km for run in recent), 1)
    prior_distance = round(sum(run.distance_km for run in prior), 1)
    return {
        "recent_runs": len(recent),
        "recent_distance_km": recent_distance,
        "prior_distance_km": prior_distance,
        "load_change_percent": round(((recent_distance - prior_distance) / prior_distance) * 100, 1) if prior_distance else None,
        "recent_elevation_m": sum(run.elevation_gain_m for run in recent),
        "recent_average_pace": format_pace(analysis.avg_pace_min_km(recent)) if recent else None,
    }


def _has_red_flags(payload: dict) -> bool:
    notes = str(payload.get("notes", "")).lower()
    severe_pain = payload.get("pain_level", 0) >= 9
    serious_sensation = bool({"numb", "tingling"} & set(payload.get("sensation", [])))
    return severe_pain or serious_sensation or any(term in notes for term in RED_FLAG_TERMS)


def _safe_guidance(payload: dict, context: dict, urgent: bool) -> str:
    areas = ", ".join(area.replace("_", " ") for area in payload["body_areas"])
    if urgent:
        return (
            "Urgent safety check: your answers may indicate a symptom that needs prompt in-person "
            "medical assessment. Stop running for now. Seek urgent care or emergency help now for chest "
            "pain, breathing trouble, new weakness/numbness, loss of bladder or bowel control, deformity, "
            "or inability to bear weight. This app cannot assess an injury remotely."
        )
    load_note = ""
    if context.get("load_change_percent") is not None:
        load_note = f" Your recent logged distance changed {context['load_change_percent']:+.0f}% versus the prior set of runs."
    return (
        f"For {areas}, reduce or pause painful running for 48–72 hours and keep all movement below pain-provoking levels."
        f" Consider gentle, comfortable mobility, sleep, hydration, and low-impact cross-training only if it is pain-free.{load_note} "
        "Avoid speed work, hills, and pushing through sharp or worsening pain. Resume gradually only after daily activities "
        "and easy movement are comfortable; a licensed clinician or physical therapist can provide an individual assessment. "
        "This is educational information, not a diagnosis, treatment plan, or emergency care."
    )


def _ai_guidance(payload: dict, context: dict) -> str | None:
    """Use an optional OpenAI-compatible chat endpoint; failure always falls back safely."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    prompt = (
        "Give concise, conservative educational running-recovery guidance. Never diagnose, prescribe, or claim certainty. "
        "Include possible common causes, training-load observations, recovery steps, a gradual return idea, avoid-for-now items, "
        "red flags, and a medical disclaimer. Data: " + json.dumps({"checkin": payload, "training": context})
    )
    try:
        import requests
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), "messages": [{"role": "system", "content": "You are a cautious running-recovery education assistant."}, {"role": "user", "content": prompt}], "temperature": 0.25, "max_tokens": 600},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None


@app.route("/api/recovery/checkins", methods=["POST"])
def create_recovery_checkin():
    if not session.get("authenticated"):
        return jsonify(error="Authentication required."), 401
    timestamps = [stamp for stamp in session.get("recovery_requests", []) if datetime.now(timezone.utc).timestamp() - stamp < AI_RATE_WINDOW_SECONDS]
    if len(timestamps) >= AI_RATE_LIMIT:
        return jsonify(error="Recovery guidance is limited to 5 requests per hour. Please try again later."), 429
    payload = request.get_json(silent=True) or {}
    body_areas = payload.get("body_areas", [])
    sensation = payload.get("sensation", [])
    triggers = payload.get("triggers", [])
    try:
        pain_level = int(payload.get("pain_level"))
    except (TypeError, ValueError):
        return jsonify(error="Choose a pain level from 1 to 10."), 400
    if not body_areas or not set(body_areas).issubset(BODY_AREAS) or not 1 <= pain_level <= 10:
        return jsonify(error="Select at least one valid body area and a pain level from 1 to 10."), 400
    if (
        not set(sensation).issubset(SENSATIONS)
        or not set(triggers).issubset(TRIGGERS)
        or payload.get("onset", "gradual") not in ONSET_OPTIONS
        or payload.get("side", "both") not in BODY_SIDES
    ):
        return jsonify(error="One or more symptom fields are invalid."), 400
    payload = {"body_areas": body_areas, "pain_level": pain_level, "onset": str(payload.get("onset", "gradual"))[:20], "sensation": sensation, "triggers": triggers, "side": str(payload.get("side", "both")), "location_detail": str(payload.get("location_detail", "")).strip()[:240], "notes": str(payload.get("notes", "")).strip()[:1000]}
    context = _training_context(_all_runs())
    urgent = _has_red_flags(payload)
    guidance = _safe_guidance(payload, context, urgent)
    if not urgent:
        guidance = _ai_guidance(payload, context) or guidance
    recovery_store.save(RecoveryCheckin(id=secrets.token_urlsafe(10), training_context=context, guidance=guidance, urgent=urgent, created_at=datetime.now(timezone.utc).isoformat(), **payload))
    timestamps.append(datetime.now(timezone.utc).timestamp())
    session["recovery_requests"] = timestamps
    return jsonify(guidance=guidance, urgent=urgent, training_context=context)


def _pace_chart_html(runs: list[Run]) -> str:
    by_source: dict[str, list[Run]] = {}
    for r in runs:
        by_source.setdefault(r.source, []).append(r)

    fig = go.Figure()
    for source, source_runs in by_source.items():
        ordered = sorted(source_runs, key=lambda r: r.date)
        color = SOURCE_COLORS.get(source, "#42f4e8")
        fig.add_trace(
            go.Scatter(
                x=[r.date.isoformat() for r in ordered],
                y=[r.avg_pace_min_km for r in ordered],
                mode="lines+markers",
                name=source.upper(),
                line=dict(color=color, width=2),
                marker=dict(color=color, size=9, line=dict(color="#ffffff", width=2)),
            )
        )
    fig.update_yaxes(autorange="reversed", title="Pace (min/km)", gridcolor="#e8e8e8", linecolor="#e8e8e8")
    fig.update_xaxes(gridcolor="#e8e8e8", linecolor="#e8e8e8")
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        height=380,
        font=dict(family="Oswald, Barlow, sans-serif", size=13, color="#111111"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn", div_id="pace-chart")


def _build_calendar(year: int, month: int, runs: list[Run], races: list[Race]) -> list[list[dict]]:
    today = date.today()
    runs_by_date = {r.date: r for r in runs}
    races_by_date = {r.date: r for r in races}
    nearest_race_date = next((r.date for r in races if r.date >= today), None)
    schedule = analysis.weekly_schedule(today, nearest_race_date)

    weeks = []
    for week in pycalendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
        days = []
        for day in week:
            run = runs_by_date.get(day)
            race = races_by_date.get(day)
            days.append(
                {
                    "date": day,
                    "in_month": day.month == month,
                    "is_today": day == today,
                    "run": run,
                    "race": race,
                    "suggested": schedule.get(day.weekday()) if day >= today and not run and not race else None,
                }
            )
        weeks.append(days)
    return weeks


def _feedback_runs(
    runs: list[Run],
    feedback_by_run: dict[str, Feedback],
    dismissed: set[str],
    today: date | None = None,
) -> list[Run]:
    """Keep saved feedback visible and expire unanswered prompts after seven days."""
    today = today or date.today()
    cutoff = today - timedelta(days=7)
    return [
        run
        for run in runs
        if run.id in feedback_by_run or (run.id not in dismissed and run.date >= cutoff)
    ]


def _dashboard_context() -> dict:
    runs = _all_runs()
    feedback_by_run = feedback_store.load_all()
    races = race_store.load_all()
    checkins = recovery_store.load_all()
    readiness = training_load.calculate(runs, feedback_by_run, checkins)

    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
        first_of_month = date(year, month, 1)
    except ValueError:
        year, month = today.year, today.month
        first_of_month = date(year, month, 1)

    prev_month = (first_of_month - timedelta(days=1)).replace(day=1)
    next_month = (first_of_month + timedelta(days=32)).replace(day=1)

    context = {
        "strava_connected": strava_client.is_configured(),
        "coros_connected": coros_client.is_configured(),
        "runs": runs,
        "feedback_by_run": feedback_by_run,
        "feedback_runs": _feedback_runs(runs, feedback_by_run, feedback_store.load_dismissed(), today),
        "feedback_expiry_days": 7,
        "races": races,
        "calendar_weeks": _build_calendar(year, month, runs, races),
        "month_label": first_of_month.strftime("%B %Y"),
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
        "recovery_checkins": checkins[:5],
        "recovery_context": _training_context(runs),
        "readiness": readiness,
        "today_run": planning.todays_run(runs, readiness, races),
        "plan_actual": planning.plan_vs_actual(runs, races, training_store.load_all(), feedback_by_run=feedback_by_run),
        "today_saved": training_store.load_all().get(today.isoformat()),
        "race_goal": race_prediction.goal_center(races, runs),
        "personal_records": personal_records.calculate(runs),
        "recovery_trends": recovery_trends.summarize(checkins),
        "shoes": shoe_store.with_mileage(runs, feedback_by_run),
        "shoe_assignments": shoe_store.assignments(),
        "sample_data": bool(runs) and all("sample" in run.id for run in runs),
    }

    if not runs:
        return context

    model = workout_model.train(list(feedback_by_run.values()))
    nearest_race_date = next((r.date for r in races if r.date >= today), None)

    context.update(
        total_distance=analysis.weekly_mileage_km(runs),
        avg_pace=format_pace(analysis.avg_pace_min_km(runs)),
        run_count=len(runs),
        chart_html=_pace_chart_html(runs),
        feedback=analysis.generate_feedback(runs),
        workouts=analysis.generate_next_workouts(runs, model=model, nearest_race_date=nearest_race_date),
    )
    return context


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8502)))
