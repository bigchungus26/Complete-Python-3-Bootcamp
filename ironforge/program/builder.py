"""Program builder — orchestrates all engine modules into a complete Program."""

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
from ironforge.program.models import Program, ProgramWeek, ProgramSession


def build_program(profile: UserProfile) -> Program:
    """Build a complete training program from a user profile."""
    # Step 1: Classify training level per movement pattern
    levels = classify(profile)

    # Step 2: Compute volume targets
    volume_targets = compute_volume(profile, levels)

    # Step 3: Plan frequency and split
    split = plan_frequency(profile, volume_targets)

    # Step 4: Build Week 1 sessions
    sessions: list[ProgramSession] = []
    # Track variant counter per muscle focus signature so A/B sessions differ
    focus_seen: dict[tuple, int] = {}
    for i, template in enumerate(split.sessions):
        focus_key = tuple(sorted(m.name for m in template.muscle_focus))
        variant = focus_seen.get(focus_key, 0)
        focus_seen[focus_key] = variant + 1

        exercises = select_exercises_for_session(
            template=template,
            all_sessions=split.sessions,
            profile=profile,
            levels=levels,
            volume_targets=volume_targets,
            session_variant=variant,
        )

        # Apply superset pairing if user wants it
        if profile.prefers_supersets:
            exercises = pair_supersets(exercises, allow_supersets=True)

        sessions.append(ProgramSession(
            day_label=template.day_label,
            exercises=exercises,
        ))

    week1 = ProgramWeek(week_number=1, sessions=sessions)

    # Step 5: Build progression and deload instructions
    progression = build_progression_instructions(profile, levels)
    deload = build_deload_instructions(profile)
    meso_overview = build_mesocycle_overview(profile, levels)

    return Program(
        level_assessment=levels,
        volume_targets=volume_targets,
        split_name=split.name,
        split_rationale=split.rationale,
        week1=week1,
        progression_instructions=progression,
        deload_instructions=deload,
        mesocycle_overview=meso_overview,
    )
