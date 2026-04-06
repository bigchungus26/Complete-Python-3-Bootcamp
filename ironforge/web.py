"""Flask web frontend for Ironforge."""

import csv
import hashlib
import io
import os
import secrets
import time
from collections import defaultdict
from functools import wraps

from flask import (
    Flask, render_template, request, Response, session, jsonify, abort,
    after_this_request, redirect, url_for,
)
from markupsafe import escape

from ironforge.data.muscle_groups import (
    Goal, Sex, CaloricPhase, EquipmentAccess, Equipment,
    VolumeMuscle,
)
from ironforge.intake.profile import UserProfile
from ironforge.engine.frequency import get_split_options, ALL_SPLITS
from ironforge.program.builder import build_program
from ironforge.program.models import Program

app = Flask(__name__)
app.secret_key = os.environ.get("IRONFORGE_SECRET_KEY", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("IRONFORGE_HTTPS", "false").lower() == "true",
    PERMANENT_SESSION_LIFETIME=3600,
)


# ─── Security Headers ────────────────────────────────────────────────────────

@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )
    return response


# ─── CSRF Protection ─────────────────────────────────────────────────────────

def _generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = _generate_csrf_token


def _check_csrf():
    """Validate CSRF token on state-changing requests."""
    token = session.get("_csrf_token")
    form_token = request.form.get("_csrf_token")
    if not token or not form_token or not secrets.compare_digest(token, form_token):
        abort(403, description="Invalid or missing CSRF token.")


# ─── Rate Limiting ────────────────────────────────────────────────────────────

_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 20  # max requests per window
RATE_WINDOW = 60  # seconds


def _rate_limit():
    """Simple in-memory rate limiter by IP."""
    ip = request.remote_addr or "unknown"
    now = time.monotonic()
    # Prune old entries
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < RATE_WINDOW]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        abort(429, description="Too many requests. Please wait a minute.")
    _rate_store[ip].append(now)


@app.before_request
def before_request_checks():
    _rate_limit()
    if request.method == "POST":
        _check_csrf()


# ─── Per-Session Program Storage ──────────────────────────────────────────────
# Store serialized program data in the session instead of a global variable.
# This prevents data leaking between users and race conditions.

_session_programs: dict[str, Program] = {}


def _store_program(program: Program) -> str:
    """Store program keyed by session ID, return the key."""
    sid = session.get("_sid")
    if not sid:
        sid = secrets.token_hex(16)
        session["_sid"] = sid
    _session_programs[sid] = program
    # Evict old entries if store grows too large (simple LRU-ish)
    if len(_session_programs) > 500:
        oldest_keys = list(_session_programs.keys())[:250]
        for k in oldest_keys:
            _session_programs.pop(k, None)
    return sid


def _get_program() -> Program | None:
    sid = session.get("_sid")
    if sid:
        return _session_programs.get(sid)
    return None


# ─── Input Validation ─────────────────────────────────────────────────────────

# Whitelists for validated inputs
VALID_GOALS = {"a", "b", "c", "d"}
VALID_CALORIC = {"surplus", "deficit", "maintenance"}
VALID_TRAINING = {"a", "b", "c"}
VALID_PROGRESSION = {"a", "b", "c"}
VALID_DAYS = {3, 4, 5, 6}
VALID_MINUTES = {40, 52, 67, 82, 95}
VALID_SUPERSETS = {"yes", "no", "no_pref"}
VALID_EQUIP = {"a", "b", "c", "d"}
VALID_SEX = {"male", "female"}
VALID_MUSCLES = {m.name for m in VolumeMuscle}

MAX_TEXT_LEN = 500


def _clean_text(value: str, max_len: int = MAX_TEXT_LEN) -> str:
    """Truncate and strip text input."""
    return value.strip()[:max_len]


def _safe_int(value: str, default: int, lo: int, hi: int) -> int:
    """Parse int with bounds, return default on failure."""
    try:
        n = int(value)
        return max(lo, min(hi, n))
    except (ValueError, TypeError):
        return default


def _parse_profile(form) -> UserProfile:
    """Parse and validate form data into a UserProfile."""
    profile = UserProfile()

    # Goals — whitelist
    goal_key = form.get("primary_goal", "a")
    if goal_key not in VALID_GOALS:
        goal_key = "a"
    profile.primary_goal = {
        "a": Goal.HYPERTROPHY, "b": Goal.STRENGTH,
        "c": Goal.HYBRID, "d": Goal.RECOMP,
    }[goal_key]

    # Priority muscles — whitelist against enum names
    for val in form.getlist("priority_muscles"):
        if val in VALID_MUSCLES:
            muscle = VolumeMuscle[val]
            if muscle not in profile.priority_muscles:
                profile.priority_muscles.append(muscle)
    if VolumeMuscle.GLUTES in profile.priority_muscles:
        profile.wants_glute_focus = True

    caloric = form.get("caloric_phase", "maintenance")
    if caloric not in VALID_CALORIC:
        caloric = "maintenance"
    profile.caloric_phase = {
        "surplus": CaloricPhase.SURPLUS,
        "deficit": CaloricPhase.DEFICIT,
        "maintenance": CaloricPhase.MAINTENANCE,
    }[caloric]

    # Training history — whitelist
    training = form.get("training_months", "b")
    if training not in VALID_TRAINING:
        training = "b"
    profile.training_months = {"a": 3, "b": 18, "c": 48}[training]

    progression = form.get("progression_rate", "b")
    if progression not in VALID_PROGRESSION:
        progression = "b"
    if progression == "a":
        profile.can_add_weight_every_session = True
    elif progression == "b":
        profile.adds_weight_every_1_2_weeks = True

    # Schedule — bounded ints + whitelist
    days = _safe_int(form.get("days_per_week", "4"), 4, 3, 6)
    if days not in VALID_DAYS:
        days = 4
    profile.days_per_week = days

    minutes = _safe_int(form.get("session_minutes", "67"), 67, 30, 120)
    if minutes not in VALID_MINUTES:
        minutes = 67
    profile.session_minutes = minutes

    supersets = form.get("prefers_supersets", "yes")
    if supersets not in VALID_SUPERSETS:
        supersets = "yes"
    profile.prefers_supersets = supersets in ("yes", "no_pref")

    # Split selection — validate against known keys
    split_key = form.get("split_key", "")
    if split_key and split_key not in ALL_SPLITS:
        split_key = ""
    profile.split_key = split_key

    # Equipment — whitelist
    equip = form.get("equipment_access", "a")
    if equip not in VALID_EQUIP:
        equip = "a"
    profile.equipment_access = {
        "a": EquipmentAccess.FULL_GYM,
        "b": EquipmentAccess.LIMITED_GYM,
        "c": EquipmentAccess.HOME_GYM,
        "d": EquipmentAccess.OTHER,
    }[equip]
    if profile.equipment_access == EquipmentAccess.HOME_GYM:
        profile.available_equipment = {
            Equipment.BARBELL, Equipment.DUMBBELL,
            Equipment.EZ_BAR, Equipment.BODYWEIGHT,
        }
    elif profile.equipment_access == EquipmentAccess.LIMITED_GYM:
        profile.available_equipment = {
            Equipment.BARBELL, Equipment.DUMBBELL,
            Equipment.CABLE, Equipment.EZ_BAR,
            Equipment.BODYWEIGHT, Equipment.MACHINE,
        }

    # Individual — whitelist + bounded text
    sex = form.get("sex", "male")
    if sex not in VALID_SEX:
        sex = "male"
    profile.sex = {"male": Sex.MALE, "female": Sex.FEMALE}[sex]

    injuries = _clean_text(form.get("injuries", ""))
    if injuries and injuries.lower() not in ("none", "no", "n/a", ""):
        profile.injuries = [injuries]

    profile.current_sets_per_muscle = _safe_int(
        form.get("current_sets", "0"), 0, 0, 50
    )
    profile.current_program = _clean_text(
        form.get("current_program", "starting fresh")
    )

    return profile


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    from ironforge.engine.frequency import SPLITS_BY_DAYS
    return render_template("index.html", splits_by_days=SPLITS_BY_DAYS)


@app.route("/api/splits/<int:days>")
def api_splits(days: int):
    """Return split options for a given day count (AJAX endpoint)."""
    if days not in VALID_DAYS:
        abort(400, description="Invalid day count.")
    options = get_split_options(days)
    return jsonify([{"key": s.key, "name": s.name, "rationale": s.rationale} for s in options])


def _format_exercise_line(ex) -> str:
    """Format one exercise as 'Name\\tSETSxREPS @RIR RIR'."""
    load = ex.load
    return f"{ex.exercise.name}\t{load.sets}x{load.rep_low}-{load.rep_high} @{load.rir} RIR"


def _build_week_text(week) -> str:
    """Build tab-separated text for a single week."""
    lines = [f"Week {week.week_number}", ""]
    for sess in week.sessions:
        lines.append(sess.day_label.replace(" — ", " - "))
        # Group supersets as "Ex1 // Ex2"
        rendered_pairs: set[int] = set()
        for ex in sess.exercises:
            if ex.superset_pair_id and ex.superset_pair_id not in rendered_pairs:
                rendered_pairs.add(ex.superset_pair_id)
                partner = next(
                    (o for o in sess.exercises
                     if o.superset_pair_id == ex.superset_pair_id
                     and o.exercise.name != ex.exercise.name), None)
                if partner:
                    name = f"{ex.exercise.name} // {partner.exercise.name}"
                    load = ex.load
                    p_load = partner.load
                    rx = (f"{load.sets}x{load.rep_low}-{load.rep_high} / "
                          f"{p_load.sets}x{p_load.rep_low}-{p_load.rep_high} @{load.rir} RIR")
                    lines.append(f"{name}\t{rx}")
                else:
                    lines.append(_format_exercise_line(ex))
            elif not ex.superset_pair_id:
                lines.append(_format_exercise_line(ex))
        lines.append("")
    return "\n".join(lines)


def _build_weeks_data(program: Program) -> list[str]:
    """Build per-week text for individual copy buttons."""
    return [_build_week_text(week) for week in program.weeks]


def _group_exercises(session):
    """Pre-process exercises into a flat list of dicts for the template.
    Supersetted pairs become a single entry with is_superset=True."""
    grouped = []
    rendered_pairs: set[int] = set()
    for ex in session.exercises:
        load = ex.load
        if ex.superset_pair_id and ex.superset_pair_id not in rendered_pairs:
            rendered_pairs.add(ex.superset_pair_id)
            partner = next(
                (o for o in session.exercises
                 if o.superset_pair_id == ex.superset_pair_id
                 and o.exercise.name != ex.exercise.name), None)
            if partner:
                p = partner.load
                grouped.append({
                    "is_superset": True,
                    "name_a": ex.exercise.name,
                    "name_b": partner.exercise.name,
                    "rx_a": f"{load.sets}\u00d7{load.rep_low}-{load.rep_high}",
                    "rx_b": f"{p.sets}\u00d7{p.rep_low}-{p.rep_high}",
                    "rir": load.rir,
                })
            else:
                grouped.append({
                    "is_superset": False,
                    "name": ex.exercise.name,
                    "rx": f"{load.sets}\u00d7{load.rep_low}-{load.rep_high}",
                    "rir": load.rir, "rest": load.rest_seconds,
                    "tier": ex.tier.value, "notes": ex.notes,
                })
        elif not ex.superset_pair_id:
            grouped.append({
                "is_superset": False,
                "name": ex.exercise.name,
                "rx": f"{load.sets}\u00d7{load.rep_low}-{load.rep_high}",
                "rir": load.rir, "rest": load.rest_seconds,
                "tier": ex.tier.value, "notes": ex.notes,
            })
    return grouped


def _prepare_program(program: Program):
    """Attach grouped_exercises to each session for template rendering."""
    for week in program.weeks:
        for sess in week.sessions:
            sess.grouped_exercises = _group_exercises(sess)


@app.route("/generate", methods=["POST"])
def generate():
    profile = _parse_profile(request.form)
    program = build_program(profile)
    _store_program(program)
    _prepare_program(program)
    session["_last_form"] = dict(request.form)
    weeks_data = _build_weeks_data(program)
    return render_template("program.html", program=program, profile=profile,
                           weeks_data=weeks_data)


@app.route("/regenerate")
def regenerate():
    """Regenerate program with different exercise selections (same muscles)."""
    form_data = session.get("_last_form")
    if not form_data:
        return redirect("/")

    from werkzeug.datastructures import ImmutableMultiDict
    form = ImmutableMultiDict(form_data)
    profile = _parse_profile(form)

    # Import and use the randomized builder
    from ironforge.program.builder import build_program_randomized
    program = build_program_randomized(profile)
    _store_program(program)
    _prepare_program(program)
    weeks_data = _build_weeks_data(program)
    return render_template("program.html", program=program, profile=profile,
                           weeks_data=weeks_data)


@app.route("/export.csv")
def export_csv():
    """Export the session's program as CSV — clean 2-column format for Sheets."""
    program = _get_program()
    if program is None:
        return "No program generated yet. Go back and generate one first.", 400

    output = io.StringIO()
    writer = csv.writer(output)

    for week in program.weeks:
        writer.writerow([f"Week {week.week_number}"])
        writer.writerow([])

        for sess in week.sessions:
            label = sess.day_label.replace(" — ", " - ")
            writer.writerow([label])

            rendered_pairs: set[int] = set()
            for ex in sess.exercises:
                load = ex.load
                if ex.superset_pair_id and ex.superset_pair_id not in rendered_pairs:
                    rendered_pairs.add(ex.superset_pair_id)
                    partner = next(
                        (o for o in sess.exercises
                         if o.superset_pair_id == ex.superset_pair_id
                         and o.exercise.name != ex.exercise.name), None)
                    if partner:
                        p = partner.load
                        name = f"{ex.exercise.name} // {partner.exercise.name}"
                        rx = (f"{load.sets}x{load.rep_low}-{load.rep_high} / "
                              f"{p.sets}x{p.rep_low}-{p.rep_high} @{load.rir} RIR")
                        writer.writerow([name, rx])
                    else:
                        writer.writerow([ex.exercise.name,
                            f"{load.sets}x{load.rep_low}-{load.rep_high} @{load.rir} RIR"])
                elif not ex.superset_pair_id:
                    writer.writerow([ex.exercise.name,
                        f"{load.sets}x{load.rep_low}-{load.rep_high} @{load.rir} RIR"])

            writer.writerow([])

    csv_content = output.getvalue()
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=ironforge_program.csv"},
    )


# ─── Error Handlers ──────────────────────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message=e.description), 403


@app.errorhandler(429)
def rate_limited(e):
    return render_template("error.html", code=429, message=e.description), 429


@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message=e.description), 400


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500,
                           message="Something went wrong. Please try again."), 500


# ─── Entry Point ─────────────────────────────────────────────────────────────

def run():
    debug = os.environ.get("IRONFORGE_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)


if __name__ == "__main__":
    run()
