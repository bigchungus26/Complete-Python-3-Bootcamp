"""Flask web frontend for Ironforge."""

from flask import Flask, render_template, request
from ironforge.data.muscle_groups import (
    Goal, Sex, CaloricPhase, EquipmentAccess, Equipment,
    VolumeMuscle,
)
from ironforge.intake.profile import UserProfile
from ironforge.intake.flow import _parse_priority_muscles
from ironforge.program.builder import build_program
from ironforge.output.formatter import render as render_text

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    form = request.form

    # Parse form into UserProfile
    profile = UserProfile()

    # Goals
    profile.primary_goal = {
        "a": Goal.HYPERTROPHY, "b": Goal.STRENGTH,
        "c": Goal.HYBRID, "d": Goal.RECOMP,
    }.get(form.get("primary_goal", "a"), Goal.HYPERTROPHY)

    priority_text = form.get("priority_muscles", "")
    profile.priority_muscles = _parse_priority_muscles(priority_text)
    if VolumeMuscle.GLUTES in profile.priority_muscles:
        profile.wants_glute_focus = True

    profile.caloric_phase = {
        "surplus": CaloricPhase.SURPLUS,
        "deficit": CaloricPhase.DEFICIT,
        "maintenance": CaloricPhase.MAINTENANCE,
    }.get(form.get("caloric_phase", "maintenance"), CaloricPhase.MAINTENANCE)

    # Training history
    profile.training_months = {
        "a": 3, "b": 18, "c": 48,
    }.get(form.get("training_months", "b"), 18)

    progression = form.get("progression_rate", "b")
    if progression == "a":
        profile.can_add_weight_every_session = True
    elif progression == "b":
        profile.adds_weight_every_1_2_weeks = True

    # Schedule
    profile.days_per_week = int(form.get("days_per_week", "4"))
    profile.session_minutes = int(form.get("session_minutes", "60"))
    profile.prefers_supersets = form.get("prefers_supersets", "yes") in ("yes", "no_pref")

    # Equipment
    equip_access = form.get("equipment_access", "a")
    profile.equipment_access = {
        "a": EquipmentAccess.FULL_GYM,
        "b": EquipmentAccess.LIMITED_GYM,
        "c": EquipmentAccess.HOME_GYM,
        "d": EquipmentAccess.OTHER,
    }.get(equip_access, EquipmentAccess.FULL_GYM)

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

    # Individual
    profile.sex = {
        "male": Sex.MALE, "female": Sex.FEMALE,
    }.get(form.get("sex", "male"), Sex.MALE)

    injuries = form.get("injuries", "").strip()
    if injuries and injuries.lower() not in ("none", "no", "n/a", ""):
        profile.injuries = [injuries]

    try:
        profile.current_sets_per_muscle = int(form.get("current_sets", "0"))
    except ValueError:
        profile.current_sets_per_muscle = 0

    profile.current_program = form.get("current_program", "starting fresh")

    # Build program
    program = build_program(profile)

    return render_template("program.html", program=program, profile=profile)


def run():
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    run()
