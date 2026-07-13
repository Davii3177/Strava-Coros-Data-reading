import calendar as pycalendar
import hmac
import os
import secrets
from datetime import date, datetime, timedelta, timezone

import plotly.graph_objects as go
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, session, url_for

import analysis
import coros_client
import feedback_store
import race_store
import strava_client
import workout_model
from models import Feedback, Race, Run, format_pace

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
    return redirect(url_for("index"))


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

    race_store.save(Race(date=race_date, name=name, distance_km=distance_km))
    return redirect(url_for("index"))


@app.route("/races/<date_str>/delete", methods=["POST"])
def delete_race(date_str):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    race_store.delete(date_str)
    return redirect(url_for("index"))


def _all_runs() -> list[Run]:
    runs = strava_client.fetch_runs() + coros_client.fetch_runs()
    runs.sort(key=lambda r: r.date, reverse=True)
    return runs


# Validated (CVD-safe, contrast-checked on both the light and dark surfaces
# in style.css) categorical colors, one per data source. Kept separate from
# the UI accent color so chart identity never gets confused with brand chrome.
SOURCE_COLORS = {"strava": "#3987e5", "coros": "#d95926"}


def _pace_chart_html(runs: list[Run]) -> str:
    by_source: dict[str, list[Run]] = {}
    for r in runs:
        by_source.setdefault(r.source, []).append(r)

    fig = go.Figure()
    for source, source_runs in by_source.items():
        ordered = sorted(source_runs, key=lambda r: r.date)
        color = SOURCE_COLORS.get(source, "#e0207c")
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


def _dashboard_context() -> dict:
    runs = _all_runs()
    feedback_by_run = feedback_store.load_all()
    races = race_store.load_all()

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
        "races": races,
        "calendar_weeks": _build_calendar(year, month, runs, races),
        "month_label": first_of_month.strftime("%B %Y"),
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
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
