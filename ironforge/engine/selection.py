"""Exercise selection engine — picks exercises per session with fractional set accounting."""

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
from ironforge.data.constants import PER_SESSION_DIRECT_CEILING, MAX_SETS_PER_EXERCISE
from ironforge.engine.frequency import SessionTemplate
from ironforge.engine.load import assign_loading
from ironforge.intake.profile import UserProfile
from ironforge.program.models import ProgrammedExercise, VolumeTarget


def _available(exercises: list[ExerciseDefinition], equip: set[Equipment]) -> list[ExerciseDefinition]:
    """Filter exercises to those usable with available equipment."""
    return [e for e in exercises if any(eq in equip for eq in e.equipment)]


def _pick(options: list[ExerciseDefinition], equip: set[Equipment],
          exclude: set[str] | None = None) -> ExerciseDefinition | None:
    """Pick first available exercise, respecting equipment and exclusions."""
    exclude = exclude or set()
    avail = [e for e in options if
             any(eq in equip for eq in e.equipment) and e.name not in exclude]
    return avail[0] if avail else None


def _sets_for_muscle(
    muscle: VolumeMuscle,
    targets: list[VolumeTarget],
    num_sessions_hitting: int,
) -> int:
    """Calculate how many direct sets to program per session for a muscle."""
    for t in targets:
        if t.muscle == muscle:
            per_session = t.working / max(num_sessions_hitting, 1)
            return max(2, min(int(round(per_session)), PER_SESSION_DIRECT_CEILING))
    return 3


def _count_muscle_in_sessions(
    muscle: VolumeMuscle,
    all_sessions: list[SessionTemplate],
) -> int:
    """Count how many sessions in the split hit a given muscle."""
    return sum(1 for s in all_sessions if muscle in s.muscle_focus)


def select_exercises_for_session(
    template: SessionTemplate,
    all_sessions: list[SessionTemplate],
    profile: UserProfile,
    levels: dict,
    volume_targets: list[VolumeTarget],
    session_variant: int = 0,
) -> list[ProgrammedExercise]:
    """Select exercises for a single session based on muscle focus and rules."""
    equip = profile.available_equipment
    exercises: list[ProgrammedExercise] = []
    used_names: set[str] = set()
    overall = profile.overall_level

    def _add(ex: ExerciseDefinition | None, muscle: VolumeMuscle,
             sets: int | None = None, notes: str = "") -> bool:
        if ex is None or ex.name in used_names:
            return False
        if sets is None:
            n_sessions = _count_muscle_in_sessions(muscle, all_sessions)
            sets = _sets_for_muscle(muscle, volume_targets, n_sessions)
        sets = min(sets, MAX_SETS_PER_EXERCISE)
        load = assign_loading(ex.tier, overall, profile.sex)
        # Avoid duplicate note fragments
        note_parts = []
        if notes:
            note_parts.append(notes)
        elif ex.notes:
            note_parts.append(ex.notes)
        all_notes = "; ".join(note_parts)
        exercises.append(ProgrammedExercise(
            exercise=ex, load=load, tier=ex.tier, notes=all_notes,
        ))
        used_names.add(ex.name)
        return True

    is_a = session_variant % 2 == 0  # A vs B variant

    # ─── CHEST ───────────────────────────────────────────────────────
    if VolumeMuscle.CHEST in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.CHEST, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.CHEST, volume_targets, n_sessions)

        # Must include at least one press + one fly
        # Alternate upper/flat between A and B sessions
        if is_a:
            press_options = [INCLINE_BENCH, INCLINE_SMITH_BENCH, INCLINE_DB_PRESS,
                            INCLINE_MACHINE_PRESS]
            fly_options = [UPPER_CHEST_PEC_DECK, UPPER_CHEST_CABLE_FLY]
        else:
            press_options = [FLAT_BENCH, SMITH_CHEST_PRESS, FLAT_DB_PRESS,
                            CHEST_PRESS_MACHINE]
            fly_options = [PEC_DECK, MID_CHEST_CABLE_FLY, LOW_CHEST_CABLE_FLY]

        press = _pick(press_options, equip, used_names)
        fly = _pick(fly_options, equip, used_names)

        press_sets = max(3, total_sets - 3) if total_sets > 5 else max(2, total_sets - 2)
        fly_sets = total_sets - press_sets if press else total_sets

        _add(press, VolumeMuscle.CHEST, sets=min(press_sets, MAX_SETS_PER_EXERCISE))
        _add(fly, VolumeMuscle.CHEST, sets=min(fly_sets, MAX_SETS_PER_EXERCISE))

    # ─── BACK ────────────────────────────────────────────────────────
    if VolumeMuscle.BACK in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.BACK, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.BACK, volume_targets, n_sessions)

        # Must include vertical pull + horizontal row + stretch-focused lat
        if is_a:
            vpull_options = [LAT_PULLDOWN_WIDE, LAT_PULLDOWN_MACHINE,
                            LAT_PULLDOWN_NEUTRAL]
            row_options = [SEATED_CHEST_SUPPORTED_ROW, CHEST_SUPPORTED_ELBOWS_TUCKED,
                          ROW_MACHINE]
        else:
            vpull_options = [LAT_PULLDOWN_NEUTRAL, LAT_PULLDOWN_CLOSE,
                            LAT_PULLDOWN_MACHINE]
            row_options = [DB_ROW_TO_HIP, CHEST_SUPPORTED_ELBOWS_FLARED,
                          TBAR_ROW, BARBELL_ROW, SMITH_BARBELL_ROW]

        stretch_options = [EZ_BAR_CABLE_PULLOVER, SINGLE_ARM_CABLE_PULLOVER,
                          FLAT_PULLOVER_MACHINE]

        vpull = _pick(vpull_options, equip, used_names)
        row = _pick(row_options, equip, used_names)
        stretch = _pick(stretch_options, equip, used_names)

        per_ex = max(2, total_sets // 3)
        _add(vpull, VolumeMuscle.BACK, sets=min(per_ex, MAX_SETS_PER_EXERCISE),
             notes="Depress scapulae first, then pull; allow full protraction at top")
        _add(row, VolumeMuscle.BACK, sets=min(per_ex, MAX_SETS_PER_EXERCISE),
             notes="Allow full scapular protraction at stretch")
        _add(stretch, VolumeMuscle.BACK,
             sets=min(max(2, total_sets - 2 * per_ex), MAX_SETS_PER_EXERCISE),
             notes="Stretch-focused lat exercise")

    # ─── SIDE/REAR DELTS ─────────────────────────────────────────────
    if VolumeMuscle.SIDE_REAR_DELTS in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.SIDE_REAR_DELTS, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.SIDE_REAR_DELTS, volume_targets, n_sessions)

        # 70-90% side delt, rest rear delt
        side_sets = max(2, int(round(total_sets * 0.75)))
        rear_sets = max(2, total_sets - side_sets)

        side_options = [LATERAL_RAISE_CABLE, LATERAL_RAISE, LATERAL_RAISE_MACHINE]
        rear_options = [REAR_DELT_FLY_SUPPORTED, REAR_DELT_FLY]

        side = _pick(side_options, equip, used_names)
        rear = _pick(rear_options, equip, used_names)

        _add(side, VolumeMuscle.SIDE_REAR_DELTS, sets=min(side_sets, MAX_SETS_PER_EXERCISE),
             notes="Neutral grip (thumbs forward); slight scaption 15-30°")
        _add(rear, VolumeMuscle.SIDE_REAR_DELTS, sets=min(rear_sets, MAX_SETS_PER_EXERCISE))

    # ─── TRICEPS ─────────────────────────────────────────────────────
    if VolumeMuscle.TRICEPS in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.TRICEPS, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.TRICEPS, volume_targets, n_sessions)

        # Must include at least one overhead movement (long head)
        oh_options = [OH_ROPE_TRICEP_EXT, OH_STRAIGHT_BAR_TRICEP_EXT,
                      OH_VBAR_TRICEP_EXT, OH_SINGLE_ARM_DB_EXT, OH_EZ_BAR_TRICEP_EXT]
        pushdown_options = [ROPE_TRICEP_EXT, VBAR_TRICEP_EXT, STRAIGHT_BAR_TRICEP_EXT]

        oh = _pick(oh_options, equip, used_names)
        pd = _pick(pushdown_options, equip, used_names)

        oh_sets = max(2, (total_sets + 1) // 2)
        pd_sets = max(2, total_sets - oh_sets)

        _add(oh, VolumeMuscle.TRICEPS, sets=min(oh_sets, MAX_SETS_PER_EXERCISE),
             notes="~40% more total triceps growth than pushdowns")
        if total_sets > 3:
            _add(pd, VolumeMuscle.TRICEPS, sets=min(pd_sets, MAX_SETS_PER_EXERCISE))

    # ─── BICEPS ──────────────────────────────────────────────────────
    if VolumeMuscle.BICEPS in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.BICEPS, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.BICEPS, volume_targets, n_sessions)

        # Must include at least one proximal (stretch) curl
        if is_a:
            stretch_options = [INCLINE_DB_CURL, BAYESIAN_CURL]
            general_options = [EZ_BAR_PREACHER_CURL, MACHINE_PREACHER_CURL,
                              PREACHER_CURL, EZ_BAR_CABLE_CURL]
        else:
            stretch_options = [BAYESIAN_CURL, INCLINE_DB_CURL]
            general_options = [PREACHER_CURL, MACHINE_PREACHER_CURL,
                              STANDING_ALT_DB_CURL, EZ_BAR_CABLE_CURL]

        stretch = _pick(stretch_options, equip, used_names)
        general = _pick(general_options, equip, used_names)

        _add(stretch, VolumeMuscle.BICEPS, sets=min(max(2, total_sets // 2), MAX_SETS_PER_EXERCISE),
             notes="Stretch-position curl")
        if total_sets > 3:
            _add(general, VolumeMuscle.BICEPS,
                 sets=min(max(2, total_sets - total_sets // 2), MAX_SETS_PER_EXERCISE))

        # Brachialis work — separate from biceps
        brach_options = [HAMMER_CURL, SEATED_HAMMER_CURL]
        brach = _pick(brach_options, equip, used_names)
        if brach and n_sessions <= 3:
            _add(brach, VolumeMuscle.FOREARMS, sets=3,
                 notes="Brachialis work — do NOT count as biceps volume; 6-10 reps")

    # ─── QUADS ───────────────────────────────────────────────────────
    if VolumeMuscle.QUADS in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.QUADS, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.QUADS, volume_targets, n_sessions)

        # Mandatory: squat/press + leg extension
        if is_a:
            squat_options = [BARBELL_SQUAT, SMITH_SQUAT, HACK_SQUAT_MACHINE,
                            BELT_SQUAT, PENDULUM_SQUAT]
        else:
            squat_options = [HACK_SQUAT_MACHINE, LEG_PRESS, LEG_PRESS_LOWERED,
                            SMITH_SQUAT, BELT_SQUAT]

        squat = _pick(squat_options, equip, used_names)
        leg_ext = _pick([LEG_EXTENSION], equip, used_names)

        squat_sets = max(3, total_sets - 3) if total_sets > 5 else max(2, total_sets - 2)
        ext_sets = total_sets - squat_sets if squat else total_sets

        _add(squat, VolumeMuscle.QUADS, sets=min(squat_sets, MAX_SETS_PER_EXERCISE),
             notes="Full depth; track knee over second toe")
        _add(leg_ext, VolumeMuscle.QUADS, sets=min(ext_sets, MAX_SETS_PER_EXERCISE),
             notes="MUST use reclined backrest (40° hip flexion) for RF growth")

    # ─── HAMSTRINGS ──────────────────────────────────────────────────
    if VolumeMuscle.HAMSTRINGS in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.HAMSTRINGS, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.HAMSTRINGS, volume_targets, n_sessions)

        # Mandatory: seated curl (primary) + hip hinge (RDL/SLDL)
        curl_options = [SEATED_HAM_CURL, LYING_HAM_CURL]
        hinge_options = [RDL, SLDL]

        curl = _pick(curl_options, equip, used_names)
        hinge = _pick(hinge_options, equip, used_names)

        curl_sets = max(2, int(round(total_sets * 0.6)))
        hinge_sets = max(2, total_sets - curl_sets)

        _add(curl, VolumeMuscle.HAMSTRINGS, sets=min(curl_sets, MAX_SETS_PER_EXERCISE),
             notes="Primary hamstring exercise; 70-90% of curl volume")
        _add(hinge, VolumeMuscle.HAMSTRINGS, sets=min(hinge_sets, MAX_SETS_PER_EXERCISE),
             notes="Mandatory hip extension component")

    # ─── GLUTES ──────────────────────────────────────────────────────
    if VolumeMuscle.GLUTES in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.GLUTES, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.GLUTES, volume_targets, n_sessions)

        if profile.wants_glute_focus:
            thrust_options = [HIP_THRUST, SMITH_HIP_THRUST]
            acc_options = [BULGARIAN_SPLIT_SQUAT, GLUTE_KICKBACK, KICKBACK_MACHINE]
            thrust = _pick(thrust_options, equip, used_names)
            acc = _pick(acc_options, equip, used_names)
            _add(thrust, VolumeMuscle.GLUTES,
                 sets=min(max(3, total_sets - 2), MAX_SETS_PER_EXERCISE),
                 notes="Mandatory for glute growth; zero hamstring CSA change")
            if total_sets > 4:
                _add(acc, VolumeMuscle.GLUTES, sets=min(3, MAX_SETS_PER_EXERCISE))
        else:
            # Glutes get volume from squats/RDLs — add hip thrust if room
            thrust_options = [HIP_THRUST, SMITH_HIP_THRUST, GLUTE_KICKBACK]
            thrust = _pick(thrust_options, equip, used_names)
            if total_sets >= 4:
                _add(thrust, VolumeMuscle.GLUTES,
                     sets=min(max(2, total_sets), MAX_SETS_PER_EXERCISE))

    # ─── CALVES ──────────────────────────────────────────────────────
    if VolumeMuscle.CALVES in template.muscle_focus:
        n_sessions = _count_muscle_in_sessions(VolumeMuscle.CALVES, all_sessions)
        total_sets = _sets_for_muscle(VolumeMuscle.CALVES, volume_targets, n_sessions)

        calf_options = [CALF_EXTENSION, DONKEY_CALF_RAISE]
        calf = _pick(calf_options, equip, used_names)
        _add(calf, VolumeMuscle.CALVES, sets=min(max(3, total_sets), MAX_SETS_PER_EXERCISE),
             notes="Post-failure lengthened partials every set; 15-20 reps")

    # ─── ABS ─────────────────────────────────────────────────────────
    if VolumeMuscle.ABS in template.muscle_focus:
        ab = _pick([AB_CURL_MACHINE], equip, used_names)
        _add(ab, VolumeMuscle.ABS, sets=3, notes="Core accessory")

    # Sort: T1 first, then T2, then T3
    exercises.sort(key=lambda e: e.tier.value)
    return exercises
