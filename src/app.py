import calendar as pycalendar
import hmac
import json
import os
import secrets
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import plotly.graph_objects as go
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, redirect, render_template, request, session, url_for

import analysis
import coros_client
import connection_store
import feedback_store
import fitbit_client
import personal_records
import planning
import race_store
import race_prediction
import recovery_store
import recovery_trends
import research_refs
import run_analysis
import shoe_store
import strava_client
import training_load
import training_store
import user_store
import workout_model
from models import Feedback, Race, RecoveryCheckin, Run, format_pace
from security import LoginRateLimiter, csrf_token, csrf_valid
from translations import translate

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Local Flask commonly runs over http; production must explicitly opt in
    # through Render's environment to avoid sending sessions over http.
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_COOKIE_SECURE", "false").lower() == "true",
)
login_limiter = LoginRateLimiter()


def _current_lang() -> str:
    lang = session.get("lang", "en")
    return lang if lang in ("en", "zh") else "en"


def t(key: str) -> str:
    return translate(key, _current_lang())


app.jinja_env.globals["t"] = t
app.jinja_env.globals["lang"] = _current_lang
app.jinja_env.globals["csrf_token"] = lambda: csrf_token(session)


@app.before_request
def protect_state_changing_requests():
    """Reject cross-site form/API writes outside the test suite."""
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"} or app.config.get("TESTING"):
        return None
    # Login is still protected by a token, but a new visitor has no session
    # until their initial GET. Return a useful error instead of silently
    # accepting a forged credential submission.
    submitted = request.headers.get("X-CSRF-Token") if request.is_json else request.form.get("csrf_token")
    if not csrf_valid(session, submitted):
        if request.is_json:
            return jsonify(error="Your form expired. Reload the page and try again."), 400
        abort(400, "Your form expired. Reload the page and try again.")


def _password_ok(entered: str) -> bool:
    expected = os.environ.get("APP_PASSWORD")
    return bool(expected) and hmac.compare_digest(entered, expected)


def _today() -> date:
    """The runner's local calendar date.

    Hosts like Render run containers in UTC. A bare `date.today()` there
    rolls over to the next day several hours before midnight in most US/EU
    timezones, so "today's run" silently shows tomorrow's workout for the
    back half of the runner's evening. RUNNER_TIMEZONE (an IANA zone name,
    e.g. "America/New_York") fixes the calendar date to where the runner
    actually is; unset or invalid falls back to the server's own local date.
    """
    tz_name = os.environ.get("RUNNER_TIMEZONE")
    if tz_name:
        try:
            return datetime.now(ZoneInfo(tz_name)).date()
        except ZoneInfoNotFoundError:
            pass
    return date.today()


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("authenticated"):
        error = None
        if request.method == "POST":
            remote = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
            if not login_limiter.allowed(remote):
                error = "Too many sign-in attempts. Please wait a few minutes and try again."
            elif user_store.has_users():
                account = user_store.authenticate(request.form.get("email", ""), request.form.get("password", ""))
                if not account:
                    login_limiter.record_failure(remote)
                    error = "Incorrect email or password."
                else:
                    session.clear()
                    session.update(authenticated=True, user_id=account["id"], user_email=account["email"])
                    csrf_token(session)
                    login_limiter.reset(remote)
                    return redirect(url_for("index"))
            elif not os.environ.get("APP_PASSWORD"):
                error = "Set APP_PASSWORD once to create the first owner account."
            elif _password_ok(request.form.get("password", "")):
                session.clear()
                session["authenticated"] = True
                csrf_token(session)
                login_limiter.reset(remote)
                return redirect(url_for("index"))
            else:
                login_limiter.record_failure(remote)
                error = "Incorrect password."
        return render_template("login.html", error=error)

    return _render_product_area("overview")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("authenticated"):
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        # The legacy secret is deliberately only a bootstrap gate. Once an
        # account exists, registration requires an explicit invite code.
        expected = os.environ.get("APP_PASSWORD") if not user_store.has_users() else os.environ.get("REGISTRATION_CODE")
        if not expected or not hmac.compare_digest(request.form.get("invite_code", ""), expected):
            error = "That setup or invitation code is not valid."
        else:
            ok, value = user_store.create_user(secrets.token_urlsafe(16), request.form.get("email", ""), request.form.get("password", ""))
            if ok:
                return redirect(url_for("index", registered="1"))
            error = value
    return render_template("register.html", error=error, first_account=not user_store.has_users())


def _render_product_area(active_area: str):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    area_titles = {
        "overview": ("area.overview.title", "area.overview.desc"),
        "training": ("area.training.title", "area.training.desc"),
        "activities": ("area.activities.title", "area.activities.desc"),
        "recovery": ("area.recovery.title", "area.recovery.desc"),
        "profile": ("area.profile.title", "area.profile.desc"),
    }
    if active_area not in area_titles:
        abort(404)
    title_key, desc_key = area_titles[active_area]
    context = _dashboard_context()
    context.update(active_area=active_area, area_title=t(title_key), area_description=t(desc_key))
    if active_area == "recovery":
        context["recovery_metrics"] = _recovery_metrics()
    return render_template("dashboard.html", **context)


@app.route("/lang/<code>")
def set_language(code):
    if code in ("en", "zh"):
        session["lang"] = code
    return redirect(request.referrer or url_for("index"))


@app.route("/training")
def training_page():
    return _render_product_area("training")


@app.route("/activities")
def activities_page():
    return _render_product_area("activities")


@app.route("/recovery")
def recovery_page():
    return _render_product_area("recovery")


@app.route("/profile")
def profile_page():
    return _render_product_area("profile")


@app.route("/connections")
def connections_page():
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    configured = {
        "strava": strava_client.is_configured(),
        "coros": coros_client.is_configured(),
        "google_health": fitbit_client.is_configured(),
    }
    return render_template("connections.html", connections=connection_store.statuses(configured))


@app.route("/connections/<provider>/sync", methods=["POST"])
def sync_connection(provider: str):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    clients = {
        "strava": strava_client,
        "coros": coros_client,
        "google_health": fitbit_client,
    }
    client = clients.get(provider)
    if client is None:
        abort(404)
    if not client.is_configured():
        return redirect(url_for("connections_page", message=f"{provider} is not configured yet."))
    try:
        runs = client.fetch_runs(limit=50)
        connection_store.record_success(provider, len(runs))
        return redirect(url_for("connections_page", message=f"{provider} sync completed."))
    except Exception:
        # Provider response bodies can contain secrets; never echo them.
        connection_store.record_failure(provider, "The provider could not be reached. Reconnect and try again.")
        return redirect(url_for("connections_page", error=f"{provider} sync failed. Reconnect and try again."))


@app.route("/how-it-works")
def how_it_works_page():
    return render_template("how_it_works.html")


@app.route("/research")
def research_page():
    return render_template("research.html")


@app.route("/logout")
def logout():
    session.clear()
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
    return redirect(url_for("activities_page") + "#feedback")


@app.route("/feedback/<run_id>/delete", methods=["POST"])
def delete_feedback(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    feedback_store.delete(run_id)
    return redirect(url_for("activities_page") + "#feedback")


@app.route("/feedback/<run_id>/dismiss", methods=["POST"])
def dismiss_feedback(run_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))

    run = next((item for item in _all_runs() if item.id == run_id), None)
    if run is None:
        abort(404)
    if run_id not in feedback_store.load_all():
        feedback_store.dismiss(run_id)
    return redirect(url_for("activities_page") + "#feedback")


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
    return redirect(url_for("training_page") + "#races")


@app.route("/races/<date_str>/delete", methods=["POST"])
def delete_race(date_str):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    race_store.delete(date_str)
    return redirect(url_for("training_page") + "#races")


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
    training_store.save(_today().isoformat(), status, distance_km, request.form.get("note", "").strip())
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
    shoe_type = request.form.get("shoe_type", "daily")
    try:
        replacement_km = float(replacement_raw) if replacement_raw else None
    except ValueError:
        abort(400)
    if replacement_km is not None and not 1 <= replacement_km <= 5000:
        abort(400)
    if shoe_type not in shoe_store.SHOE_TYPES:
        abort(400)
    shoe_store.add(brand, model, nickname, purchase_date, replacement_km, shoe_type)
    return redirect(url_for("profile_page") + "#shoes")


@app.route("/shoes/<shoe_id>/retire", methods=["POST"])
def retire_shoe(shoe_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    if not shoe_store.retire(shoe_id):
        abort(404)
    return redirect(url_for("profile_page") + "#shoes")


@app.route("/shoes/<shoe_id>/type", methods=["POST"])
def update_shoe_type(shoe_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    if not shoe_store.set_type(shoe_id, request.form.get("shoe_type", "")):
        abort(400)
    return redirect(url_for("profile_page") + "#shoes")


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
    return redirect(url_for("profile_page") + "#shoes")


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
    return redirect(url_for("recovery_page") + "#recovery-timeline")


@app.route("/recovery/<checkin_id>/dismiss", methods=["POST"])
def dismiss_recovery_checkin(checkin_id):
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    if not recovery_store.dismiss(checkin_id):
        abort(404)
    return redirect(url_for("recovery_page") + "#recovery-timeline")


@app.route("/recovery/export")
def export_recovery():
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    lines = ["Gaman recovery check-in summary", "Educational history only; not a diagnosis or treatment record.", ""]
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
    fitbit_configured = fitbit_client.is_configured()
    if not strava_configured and not coros_configured and not fitbit_configured:
        runs = strava_client.fetch_runs(limit=50) + coros_client.fetch_runs(limit=50) + fitbit_client.fetch_runs(limit=50)
    else:
        runs = []
        for provider, client, configured in (
            ("strava", strava_client, strava_configured),
            ("google_health", fitbit_client, fitbit_configured),
        ):
            if not configured:
                continue
            try:
                source_runs = client.fetch_runs(limit=50)
                runs += source_runs
                connection_store.record_success(provider, len(source_runs))
            except Exception:
                connection_store.record_failure(provider, "The provider could not be reached. Reconnect and try again.")
        if coros_configured:
            try:
                source_runs = coros_client.fetch_runs(limit=50)
                runs += source_runs
                connection_store.record_success("coros", len(source_runs))
            except NotImplementedError:
                connection_store.record_failure("coros", "COROS sync is not available yet.")
            except Exception:
                connection_store.record_failure("coros", "The provider could not be reached. Reconnect and try again.")
    runs.sort(key=lambda r: r.date, reverse=True)
    return runs


def _recovery_metrics() -> dict:
    """Objective recovery signals (sleep, resting HR, HRV) from the Google
    Health / Fitbit connection. Guarded so a Health API hiccup or an
    unconnected source never breaks the Recovery page."""
    try:
        return {
            "sleep": fitbit_client.fetch_sleep(limit=7),
            "resting_hr": fitbit_client.fetch_resting_hr(limit=14),
            "hrv": fitbit_client.fetch_hrv(limit=14),
        }
    except Exception:
        return {"sleep": [], "resting_hr": [], "hrv": []}


# Validated (CVD-safe, contrast-checked on both the light and dark surfaces
# in style.css) categorical colors, one per data source. Kept separate from
# the UI accent color so chart identity stays separate from interface actions.
SOURCE_COLORS = {"strava": "#7550a6", "coros": "#77717c", "fitbit": "#00838f"}

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
    # Region-matched educational reading from the committed literature review;
    # omitted for urgent results so the in-person care message stays the focus.
    research = research_refs.for_areas(body_areas) if not urgent else {"references": [], "research_anchors": []}
    return jsonify(guidance=guidance, urgent=urgent, training_context=context, references=research["references"], research_anchors=research["research_anchors"])


ASK_RATE_LIMIT = 20
GEMINI_MODEL_DEFAULT = "gemini-flash-lite-latest"
ASK_SYSTEM_PROMPT = (
    "You are Ask Gaman, the assistant inside the Gaman running app. You help one runner interpret their own "
    "training data and make sensible, conservative decisions: what to run today, how hard, when to rest, and "
    "how to approach an upcoming race. A JSON object with that runner's real logged data (recent runs, readiness, "
    "weekly load, today's recommended session, upcoming race, recovery notes) is included with each question. "
    "Ground every answer in that data and never invent numbers that are not present.\n\n"
    "Be brief. Start with a one-sentence direct answer or recommendation, then add at most two or three short "
    "supporting points. Stay under about 80 words. Do not write long paragraphs, and do not add headings, "
    "preambles, or sign-offs. When you list points, use simple hyphen bullets (each on its own line). You may use "
    "**bold** on a single short label if it helps, but keep formatting minimal. Write in plain, direct language.\n\n"
    "You are not a doctor — for pain, injury, or medical symptoms give only brief general education, point the "
    "runner to the Body & Recovery check-in, and suggest a clinician; never diagnose or prescribe. Favor gradual "
    "progression and recovery over pushing through warning signs."
)


def _ask_context() -> dict:
    """Compact, grounded snapshot of the runner's data for the chat model (no charts/heavy objects)."""
    runs = _all_runs()
    feedback_by_run = feedback_store.load_all()
    races = race_store.load_all()
    checkins = [checkin for checkin in recovery_store.load_all() if not checkin.dismissed]
    today = _today()
    readiness = training_load.calculate(runs, feedback_by_run, checkins, today=today)
    upcoming = next((race for race in sorted(races, key=lambda r: r.date) if race.date >= today), None)
    trends = recovery_trends.summarize(checkins)
    today_run = planning.todays_run(runs, readiness, races, today=today)
    context = {
        "today": today.isoformat(),
        "run_count": len(runs),
        "readiness": {
            "status": readiness.get("status"),
            "recent_7day_km": readiness.get("recent_km"),
            "prior_weekly_km": readiness.get("prior_weekly_km"),
            "load_change_percent": readiness.get("change_percent"),
        },
        "recent_runs": [
            {
                "date": run.date.isoformat(),
                "source": run.source,
                "distance_km": run.distance_km,
                "duration_min": run.duration_min,
                "pace": run.pace_str,
                "avg_hr": run.avg_hr,
                "elevation_gain_m": run.elevation_gain_m,
            }
            for run in runs[:8]
        ],
        "upcoming_race": (
            {"name": upcoming.name, "date": upcoming.date.isoformat(), "distance_km": upcoming.distance_km}
            if upcoming
            else None
        ),
        "recovery_trends": [
            {"area": item.get("area"), "latest": item.get("latest"), "trend": item.get("trend")}
            for item in trends.get("areas", [])
        ],
    }
    if runs:
        today_run = planning.todays_run(runs, readiness, races, today=today)
        context["todays_recommended_run"] = {
            "type": today_run.get("type"),
            "distance_km": today_run.get("distance_km"),
            "duration_min": today_run.get("duration_min"),
            "target": today_run.get("target"),
            "purpose": today_run.get("purpose"),
        }
        context["weekly_mileage_km"] = analysis.weekly_mileage_km(runs)
        context["average_pace"] = format_pace(analysis.avg_pace_min_km(runs))
    return context


def _ask_gemini(question: str, history: list[dict], context: dict) -> str | None:
    """Call Google's Gemini generateContent endpoint; any failure returns None so the caller falls back safely."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    model = os.environ.get("GEMINI_MODEL", GEMINI_MODEL_DEFAULT)
    contents = []
    for turn in history:
        text = str(turn.get("content", "")).strip()
        if not text:
            continue
        role = "model" if turn.get("role") in ("assistant", "model") else "user"
        contents.append({"role": role, "parts": [{"text": text[:2000]}]})
    contents.append(
        {"role": "user", "parts": [{"text": "My training data (JSON):\n" + json.dumps(context) + "\n\nQuestion: " + question}]}
    )
    payload = {
        "system_instruction": {"parts": [{"text": ASK_SYSTEM_PROMPT}]},
        "contents": contents,
        # gemini-3/2.5 flash are "thinking" models; disable thinking so the token
        # budget goes to the (deliberately short) answer instead of hidden
        # reasoning — keeps replies fast, cheap, concise, and never truncated.
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600, "thinkingConfig": {"thinkingBudget": 0}},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    try:
        import time
        import requests
        for attempt in range(3):
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            # Preview flash models are occasionally overloaded (503); retry briefly.
            if response.status_code == 503 and attempt < 2:
                time.sleep(1.2 * (attempt + 1))
                continue
            response.raise_for_status()
            candidates = response.json().get("candidates", [])
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()
            return text or None
        return None
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None


@app.route("/api/ask", methods=["POST"])
def ask_gaman():
    if not session.get("authenticated"):
        return jsonify(error="Authentication required."), 401
    now = datetime.now(timezone.utc).timestamp()
    timestamps = [stamp for stamp in session.get("ask_requests", []) if now - stamp < AI_RATE_WINDOW_SECONDS]
    if len(timestamps) >= ASK_RATE_LIMIT:
        return jsonify(error=f"Ask Gaman is limited to {ASK_RATE_LIMIT} questions per hour. Please try again later."), 429
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify(error="Type a question first."), 400
    question = question[:1000]
    history = payload.get("history", [])
    history = history[-8:] if isinstance(history, list) else []
    if not os.environ.get("GEMINI_API_KEY"):
        return jsonify(
            ok=False,
            answer=(
                "Ask Gaman isn’t set up yet — add a GEMINI_API_KEY on the server to enable it. In the meantime, "
                "the Overview shows your readiness, today’s recommended run, and weekly load."
            ),
        )
    answer = _ask_gemini(question, history, _ask_context())
    if not answer:
        return jsonify(ok=False, answer="Ask Gaman couldn’t answer just now. Please try again in a moment.")
    timestamps.append(now)
    session["ask_requests"] = timestamps
    return jsonify(ok=True, answer=answer)


def _pace_chart_html(runs: list[Run]) -> str:
    by_source: dict[str, list[Run]] = {}
    for r in runs:
        by_source.setdefault(r.source, []).append(r)

    fig = go.Figure()
    for source, source_runs in by_source.items():
        ordered = sorted(source_runs, key=lambda r: r.date)
        color = SOURCE_COLORS.get(source, "#7550a6")
        fig.add_trace(
            go.Scatter(
                x=[r.date.isoformat() for r in ordered],
                y=[r.avg_pace_min_km for r in ordered],
                customdata=[[f"{r.avg_hr} bpm" if r.avg_hr else "Unavailable", r.elevation_gain_m] for r in ordered],
                mode="lines+markers",
                name=source.title(),
                line=dict(color=color, width=2),
                marker=dict(color=color, size=9, line=dict(color="#fbfafc", width=1.5)),
                hovertemplate=(
                    "<b>%{x}</b><br>Pace: %{y:.2f} min/km"
                    "<br>Heart rate: %{customdata[0]}"
                    "<br>Elevation gain: %{customdata[1]} m<extra>%{fullData.name}</extra>"
                ),
            )
        )
    fig.update_yaxes(autorange="reversed", title="Average pace (min/km)", gridcolor="rgba(98,93,102,.16)", linecolor="rgba(98,93,102,.2)")
    fig.update_xaxes(title="Run date", gridcolor="rgba(98,93,102,.12)", linecolor="rgba(98,93,102,.2)")
    fig.update_layout(
        margin=dict(l=54, r=20, t=18, b=52),
        height=330,
        font=dict(family="Arial, sans-serif", size=12, color="#5f5963"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(font=dict(family="Arial, sans-serif", size=12)),
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn", div_id="pace-chart")


def _build_calendar(year: int, month: int, runs: list[Run], races: list[Race], today: date | None = None) -> list[list[dict]]:
    today = today or _today()
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
    today = today or _today()
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
    checkins = [checkin for checkin in recovery_store.load_all() if not checkin.dismissed]
    today = _today()
    readiness = training_load.calculate(runs, feedback_by_run, checkins, today=today)

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
        "fitbit_connected": fitbit_client.is_configured(),
        "connection_statuses": connection_store.statuses({
            "strava": strava_client.is_configured(),
            "coros": coros_client.is_configured(),
            "google_health": fitbit_client.is_configured(),
        }),
        "runs": runs,
        "feedback_by_run": feedback_by_run,
        "feedback_runs": _feedback_runs(runs, feedback_by_run, feedback_store.load_dismissed(), today),
        "feedback_expiry_days": 7,
        "races": races,
        "calendar_weeks": _build_calendar(year, month, runs, races, today=today),
        "month_label": first_of_month.strftime("%B %Y"),
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
        "recovery_checkins": checkins[:5],
        "recovery_context": _training_context(runs),
        "readiness": readiness,
        "today_run": today_run,
        "plan_actual": planning.plan_vs_actual(runs, races, training_store.load_all(), today=today, feedback_by_run=feedback_by_run),
        "today_saved": training_store.load_all().get(today.isoformat()),
        "race_goal": race_prediction.goal_center(races, runs, today=today),
        "personal_records": personal_records.calculate(runs),
        "recovery_trends": recovery_trends.summarize(checkins),
        "shoes": shoe_store.with_mileage(runs, feedback_by_run),
        "shoe_suggestion": shoe_store.suggest_for_today(runs, feedback_by_run, today_run["type"]),
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
        workouts=analysis.generate_next_workouts(runs, model=model, nearest_race_date=nearest_race_date, today=today),
    )
    return context


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8502)))
