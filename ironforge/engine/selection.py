"""Exercise selection engine — picks exercises per session with strict set bounds.

Rules enforced:
- Every exercise gets exactly 2 or 3 sets (never 1, never 4+)
- Weekly sets per muscle group: 4-12 (enforced via exercise count, not set count)
- Exercises are picked from the approved list filtered by equipment
"""

import random
from ironforge.data.muscle_groups import (
    MuscleGroup, VolumeMuscle, Equipment, Tier, TrainingLevel, VOLUME_MUSCLE_MAP,
)
from ironforge.data.exercises import (
    ExerciseDefinition, ALL_EXERCISES,
    # Chest
    INCLINE_BENCH, FLAT_BENCH, INCLINE_DB_PRESS, FLAT_DB_PRESS,
    INCLINE_SMITH_BENCH, SMITH_CHEST_PRESS, CHEST_PRESS_MACHINE,
    INCLINE_MACHINE_PRESS, PEC_DECK, UPPER_CHEST_PEC_DECK,
    MID_CHEST_CABLE_FLY, UPPER_CHEST_CABLE_FLY, LOW_CHEST_CABLE_FLY,
    # Shoulders
    SHOULDER_PRESS, SHOULDER_PRESS_MACHINE,
    LATERAL_RAISE, LATERAL_RAISE_CABLE, LATERAL_RAISE_MACHINE,
    REAR_DELT_FLY_SUPPORTED, REAR_DELT_FLY,
    # Triceps
    OH_ROPE_TRICEP_EXT, OH_STRAIGHT_BAR_TRICEP_EXT, OH_VBAR_TRICEP_EXT,
    OH_SINGLE_ARM_DB_EXT, OH_EZ_BAR_TRICEP_EXT,
    EZ_BAR_SKULL_CRUSHER, ROPE_TRICEP_EXT, VBAR_TRICEP_EXT,
    STRAIGHT_BAR_TRICEP_EXT,
    # Biceps
    INCLINE_DB_CURL, BAYESIAN_CURL, PREACHER_CURL, MACHINE_PREACHER_CURL,
    EZ_BAR_PREACHER_CURL, EZ_BAR_CABLE_CURL, STANDING_ALT_DB_CURL,
    HAMMER_CURL, SEATED_HAMMER_CURL,
    # Back vertical
    LAT_PULLDOWN_MACHINE, LAT_PULLDOWN_WIDE, LAT_PULLDOWN_NEUTRAL,
    LAT_PULLDOWN_CLOSE, EZ_BAR_CABLE_PULLOVER, SINGLE_ARM_CABLE_PULLOVER,
    FLAT_PULLOVER_MACHINE,
    # Back horizontal
    SEATED_CHEST_SUPPORTED_ROW, CHEST_SUPPORTED_ELBOWS_TUCKED,
    CHEST_SUPPORTED_ELBOWS_FLARED, DB_ROW_TO_HIP, ROW_MACHINE,
    TBAR_ROW, BARBELL_ROW, SMITH_BARBELL_ROW,
    SINGLE_ARM_CABLE_ROW, WIDE_GRIP_CABLE_ROW,
    # Quads
    BARBELL_SQUAT, SMITH_SQUAT, HACK_SQUAT_MACHINE, LEG_PRESS,
    LEG_PRESS_LOWERED, LEG_EXTENSION, BELT_SQUAT, PENDULUM_SQUAT,
    BULGARIAN_SPLIT_SQUAT,
    # Hamstrings
    SEATED_HAM_CURL, LYING_HAM_CURL, RDL, SLDL,
    # Glutes
    HIP_THRUST, SMITH_HIP_THRUST, GLUTE_KICKBACK, KICKBACK_MACHINE,
    # Calves
    CALF_EXTENSION, DONKEY_CALF_RAISE,
    # Additional
    AB_CURL_MACHINE, ADDUCTOR_MACHINE,
)
from ironforge.engine.frequency import SessionTemplate
from ironforge.engine.load import assign_loading
from ironforge.intake.profile import UserProfile
from ironforge.program.models import ProgrammedExercise, VolumeTarget

# ─── Set bounds ──────────────────────────────────────────────────────────────
MIN_SETS_PER_EXERCISE = 2
MAX_SETS_PER_EXERCISE = 3


def _pick(options: list[ExerciseDefinition], equip: set[Equipment],
          exclude: set[str] | None = None) -> ExerciseDefinition | None:
    exclude = exclude or set()
    for e in options:
        if any(eq in equip for eq in e.equipment) and e.name not in exclude:
            return e
    return None


def _count_muscle_in_sessions(
    muscle: VolumeMuscle, all_sessions: list[SessionTemplate],
) -> int:
    return sum(1 for s in all_sessions if muscle in s.muscle_focus)


def select_exercises_for_session(
    template: SessionTemplate,
    all_sessions: list[SessionTemplate],
    profile: UserProfile,
    levels: dict,
    volume_targets: list[VolumeTarget],
    session_variant: int = 0,
    week: int = 1,
) -> list[ProgrammedExercise]:
    """Select exercises for a single session. Every exercise gets 2 or 3 sets."""
    equip = profile.available_equipment
    exercises: list[ProgrammedExercise] = []
    used_names: set[str] = set()
    overall = profile.overall_level

    def _add(ex: ExerciseDefinition | None, sets: int = 2,
             notes: str = "") -> bool:
        if ex is None or ex.name in used_names:
            return False
        sets = max(MIN_SETS_PER_EXERCISE, min(sets, MAX_SETS_PER_EXERCISE))
        load = assign_loading(ex.tier, overall, profile.sex, week=week, sets=sets)
        note = notes if notes else (ex.notes or "")
        exercises.append(ProgrammedExercise(
            exercise=ex, load=load, tier=ex.tier, notes=note,
        ))
        used_names.add(ex.name)
        return True

    is_a = session_variant % 2 == 0

    # ─── CHEST ───────────────────────────────────────────────────────
    if VolumeMuscle.CHEST in template.muscle_focus:
        if is_a:
            press_opts = [INCLINE_BENCH, INCLINE_SMITH_BENCH, INCLINE_DB_PRESS,
                          INCLINE_MACHINE_PRESS]
            fly_opts = [UPPER_CHEST_PEC_DECK, UPPER_CHEST_CABLE_FLY]
        else:
            press_opts = [FLAT_BENCH, SMITH_CHEST_PRESS, FLAT_DB_PRESS,
                          CHEST_PRESS_MACHINE]
            fly_opts = [PEC_DECK, MID_CHEST_CABLE_FLY, LOW_CHEST_CABLE_FLY]

        _add(_pick(press_opts, equip, used_names), 3)
        _add(_pick(fly_opts, equip, used_names), 2)

    # ─── BACK ────────────────────────────────────────────────────────
    if VolumeMuscle.BACK in template.muscle_focus:
        if is_a:
            vpull_opts = [LAT_PULLDOWN_WIDE, LAT_PULLDOWN_MACHINE, LAT_PULLDOWN_NEUTRAL]
            row_opts = [SEATED_CHEST_SUPPORTED_ROW, CHEST_SUPPORTED_ELBOWS_TUCKED, ROW_MACHINE]
        else:
            vpull_opts = [LAT_PULLDOWN_NEUTRAL, LAT_PULLDOWN_CLOSE, LAT_PULLDOWN_MACHINE]
            row_opts = [DB_ROW_TO_HIP, CHEST_SUPPORTED_ELBOWS_FLARED, TBAR_ROW, BARBELL_ROW]

        stretch_opts = [EZ_BAR_CABLE_PULLOVER, SINGLE_ARM_CABLE_PULLOVER, FLAT_PULLOVER_MACHINE]

        _add(_pick(vpull_opts, equip, used_names), 3,
             "Depress scapulae first, then pull; full protraction at top")
        _add(_pick(row_opts, equip, used_names), 3,
             "Full scapular protraction at stretch")
        _add(_pick(stretch_opts, equip, used_names), 2,
             "Stretch-focused lat exercise")

    # ─── SIDE/REAR DELTS ─────────────────────────────────────────────
    if VolumeMuscle.SIDE_REAR_DELTS in template.muscle_focus:
        side_opts = [LATERAL_RAISE_CABLE, LATERAL_RAISE, LATERAL_RAISE_MACHINE]
        rear_opts = [REAR_DELT_FLY_SUPPORTED, REAR_DELT_FLY]

        _add(_pick(side_opts, equip, used_names), 3,
             "Neutral grip (thumbs forward); slight scaption 15-30°")
        _add(_pick(rear_opts, equip, used_names), 2)

    # ─── TRICEPS ─────────────────────────────────────────────────────
    if VolumeMuscle.TRICEPS in template.muscle_focus:
        oh_opts = [OH_ROPE_TRICEP_EXT, OH_STRAIGHT_BAR_TRICEP_EXT,
                   OH_VBAR_TRICEP_EXT, OH_SINGLE_ARM_DB_EXT, OH_EZ_BAR_TRICEP_EXT]
        pd_opts = [ROPE_TRICEP_EXT, VBAR_TRICEP_EXT, STRAIGHT_BAR_TRICEP_EXT]

        _add(_pick(oh_opts, equip, used_names), 3,
             "Overhead = ~40% more triceps growth than pushdowns")
        _add(_pick(pd_opts, equip, used_names), 2)

    # ─── BICEPS ──────────────────────────────────────────────────────
    if VolumeMuscle.BICEPS in template.muscle_focus:
        if is_a:
            stretch_opts = [INCLINE_DB_CURL, BAYESIAN_CURL]
            general_opts = [EZ_BAR_PREACHER_CURL, MACHINE_PREACHER_CURL, PREACHER_CURL]
        else:
            stretch_opts = [BAYESIAN_CURL, INCLINE_DB_CURL]
            general_opts = [PREACHER_CURL, STANDING_ALT_DB_CURL, EZ_BAR_CABLE_CURL]

        _add(_pick(stretch_opts, equip, used_names), 2, "Stretch-position curl")
        _add(_pick(general_opts, equip, used_names), 2)

        # Brachialis — separate, not counted as biceps
        brach_opts = [HAMMER_CURL, SEATED_HAMMER_CURL]
        _add(_pick(brach_opts, equip, used_names), 3,
             "Brachialis — do NOT count as biceps volume")

    # ─── QUADS ───────────────────────────────────────────────────────
    if VolumeMuscle.QUADS in template.muscle_focus:
        if is_a:
            squat_opts = [BARBELL_SQUAT, SMITH_SQUAT, HACK_SQUAT_MACHINE, BELT_SQUAT]
        else:
            squat_opts = [HACK_SQUAT_MACHINE, LEG_PRESS, LEG_PRESS_LOWERED, SMITH_SQUAT]

        _add(_pick(squat_opts, equip, used_names), 3,
             "Full depth; track knee over second toe")
        _add(_pick([LEG_EXTENSION], equip, used_names), 2,
             "Reclined backrest (40° hip flexion) for RF growth")

    # ─── HAMSTRINGS ──────────────────────────────────────────────────
    if VolumeMuscle.HAMSTRINGS in template.muscle_focus:
        _add(_pick([SEATED_HAM_CURL, LYING_HAM_CURL], equip, used_names), 3,
             "Primary hamstring exercise; 70-90% of curl volume")
        _add(_pick([RDL, SLDL], equip, used_names), 2,
             "Mandatory hip extension component")

    # ─── GLUTES ──────────────────────────────────────────────────────
    if VolumeMuscle.GLUTES in template.muscle_focus:
        if profile.wants_glute_focus:
            _add(_pick([HIP_THRUST, SMITH_HIP_THRUST], equip, used_names), 3,
                 "Primary glute builder")
            _add(_pick([BULGARIAN_SPLIT_SQUAT, GLUTE_KICKBACK, KICKBACK_MACHINE],
                       equip, used_names), 2)
        else:
            _add(_pick([HIP_THRUST, SMITH_HIP_THRUST, GLUTE_KICKBACK],
                       equip, used_names), 2)

    # ─── CALVES ──────────────────────────────────────────────────────
    if VolumeMuscle.CALVES in template.muscle_focus:
        _add(_pick([CALF_EXTENSION, DONKEY_CALF_RAISE], equip, used_names), 3,
             "Post-failure lengthened partials every set")

    # ─── ABS ─────────────────────────────────────────────────────────
    if VolumeMuscle.ABS in template.muscle_focus:
        _add(_pick([AB_CURL_MACHINE], equip, used_names), 3)

    # Sort: T1 first, then T2, then T3
    exercises.sort(key=lambda e: e.tier.value)
    return exercises
