"""Program builder — orchestrates all engine modules into a complete Program."""

from ironforge.data.constants import MESO_LENGTH
from ironforge.intake.profile import UserProfile
from ironforge.engine.classifier import classify
from ironforge.engine.volume import compute_volume
from ironforge.engine.frequency import plan_frequency
from ironforge.engine.selection import select_exercises_for_session
from ironforge.engine.supersets import pair_supersets
from ironforge.engine.periodization import (
    build_mesocycle_overview, build_progression_instructions,
    build_deload_instructions,
)
from ironforge.engine.substitutions import get_substitutes, is_substitutable
from ironforge.program.models import Program, ProgramWeek, ProgramSession, ProgrammedExercise

import random


def _swap_exercises(program: Program, equip: set) -> Program:
    """Swap each substitutable exercise with a random substitute from the same group."""
    # Build a swap map: old_name → new ExerciseDefinition (consistent across weeks)
    swap_map: dict[str, any] = {}
    for s in program.weeks[0].sessions:
        for ex in s.exercises:
            name = ex.exercise.name
            if name in swap_map:
                continue
            if is_substitutable(name):
                subs = [sub for sub in get_substitutes(name)
                        if any(eq in equip for eq in sub.equipment)]
                if subs:
                    swap_map[name] = random.choice(subs)

    # Apply swaps across all weeks
    for week in program.weeks:
        for s in week.sessions:
            for ex in s.exercises:
                if ex.exercise.name in swap_map:
                    new_ex_def = swap_map[ex.exercise.name]
                    ex.exercise = new_ex_def
                    ex.notes = new_ex_def.notes or ""
    return program


def build_program(profile: UserProfile) -> Program:
    """Build a complete training program from a user profile."""
    levels = classify(profile)
    volume_targets = compute_volume(profile, levels)
    split = plan_frequency(profile, volume_targets, split_key=profile.split_key or None)

    # A/B variant mapping (same exercises across all weeks)
    focus_seen: dict[tuple, int] = {}
    variant_map: list[int] = []
    for template in split.sessions:
        focus_key = tuple(sorted(m.name for m in template.muscle_focus))
        variant = focus_seen.get(focus_key, 0)
        focus_seen[focus_key] = variant + 1
        variant_map.append(variant)

    # Build 4 training weeks — same exercises/sets, only RIR changes
    all_weeks: list[ProgramWeek] = []
    for week_num in range(1, MESO_LENGTH + 1):
        sessions: list[ProgramSession] = []
        for i, template in enumerate(split.sessions):
            exercises = select_exercises_for_session(
                template=template,
                all_sessions=split.sessions,
                profile=profile,
                levels=levels,
                volume_targets=volume_targets,
                session_variant=variant_map[i],
                week=week_num,
            )
            if profile.prefers_supersets:
                exercises = pair_supersets(exercises, allow_supersets=True)
            sessions.append(ProgramSession(
                day_label=template.day_label,
                exercises=exercises,
            ))
        all_weeks.append(ProgramWeek(week_number=week_num, sessions=sessions))

    progression = build_progression_instructions(profile, levels)
    deload = build_deload_instructions(profile)
    meso_overview = build_mesocycle_overview(profile, levels)

    return Program(
        level_assessment=levels,
        volume_targets=volume_targets,
        split_name=split.name,
        split_rationale=split.rationale,
        weeks=all_weeks,
        progression_instructions=progression,
        deload_instructions=deload,
        mesocycle_overview=meso_overview,
    )


def build_program_randomized(profile: UserProfile) -> Program:
    """Build a program then swap exercises for substitutes from the same muscle region."""
    program = build_program(profile)
    return _swap_exercises(program, profile.available_equipment)
