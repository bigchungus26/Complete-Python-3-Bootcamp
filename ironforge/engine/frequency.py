"""Frequency planner — determines split structure and session templates."""

from dataclasses import dataclass, field
from ironforge.data.muscle_groups import VolumeMuscle
from ironforge.intake.profile import UserProfile
from ironforge.program.models import VolumeTarget


@dataclass
class SessionTemplate:
    day_label: str
    muscle_focus: list[VolumeMuscle] = field(default_factory=list)


@dataclass
class SplitPlan:
    name: str
    sessions: list[SessionTemplate]
    rationale: str


def _full_body_3() -> list[SessionTemplate]:
    return [
        SessionTemplate("Day 1 — Full Body A", [
            VolumeMuscle.CHEST, VolumeMuscle.BACK, VolumeMuscle.QUADS,
            VolumeMuscle.HAMSTRINGS, VolumeMuscle.SIDE_REAR_DELTS,
            VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS, VolumeMuscle.CALVES,
        ]),
        SessionTemplate("Day 2 — Full Body B", [
            VolumeMuscle.CHEST, VolumeMuscle.BACK, VolumeMuscle.QUADS,
            VolumeMuscle.HAMSTRINGS, VolumeMuscle.SIDE_REAR_DELTS,
            VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS, VolumeMuscle.CALVES,
        ]),
        SessionTemplate("Day 3 — Full Body C", [
            VolumeMuscle.CHEST, VolumeMuscle.BACK, VolumeMuscle.QUADS,
            VolumeMuscle.HAMSTRINGS, VolumeMuscle.SIDE_REAR_DELTS,
            VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS, VolumeMuscle.CALVES,
            VolumeMuscle.GLUTES, VolumeMuscle.ABS,
        ]),
    ]


def _upper_lower_4() -> list[SessionTemplate]:
    return [
        SessionTemplate("Day 1 — Upper A", [
            VolumeMuscle.CHEST, VolumeMuscle.BACK,
            VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
            VolumeMuscle.TRICEPS,
        ]),
        SessionTemplate("Day 2 — Lower A", [
            VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
            VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS,
        ]),
        SessionTemplate("Day 3 — Upper B", [
            VolumeMuscle.CHEST, VolumeMuscle.BACK,
            VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
            VolumeMuscle.TRICEPS,
        ]),
        SessionTemplate("Day 4 — Lower B", [
            VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
            VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS,
        ]),
    ]


def _ul_ppl_5(profile: UserProfile) -> list[SessionTemplate]:
    """Upper/Lower + PPL hybrid — priority muscles get 3x/week."""
    return [
        SessionTemplate("Day 1 — Upper A", [
            VolumeMuscle.CHEST, VolumeMuscle.BACK,
            VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
            VolumeMuscle.TRICEPS,
        ]),
        SessionTemplate("Day 2 — Lower A", [
            VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
            VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS,
        ]),
        SessionTemplate("Day 3 — Push", [
            VolumeMuscle.CHEST, VolumeMuscle.SIDE_REAR_DELTS,
            VolumeMuscle.TRICEPS,
        ]),
        SessionTemplate("Day 4 — Pull", [
            VolumeMuscle.BACK, VolumeMuscle.BICEPS,
            VolumeMuscle.SIDE_REAR_DELTS,
        ]),
        SessionTemplate("Day 5 — Legs", [
            VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
            VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS,
        ]),
    ]


def _ppl_6() -> list[SessionTemplate]:
    return [
        SessionTemplate("Day 1 — Push A", [
            VolumeMuscle.CHEST, VolumeMuscle.SIDE_REAR_DELTS,
            VolumeMuscle.TRICEPS,
        ]),
        SessionTemplate("Day 2 — Pull A", [
            VolumeMuscle.BACK, VolumeMuscle.BICEPS,
            VolumeMuscle.SIDE_REAR_DELTS,
        ]),
        SessionTemplate("Day 3 — Legs A", [
            VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
            VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS,
        ]),
        SessionTemplate("Day 4 — Push B", [
            VolumeMuscle.CHEST, VolumeMuscle.SIDE_REAR_DELTS,
            VolumeMuscle.TRICEPS,
        ]),
        SessionTemplate("Day 5 — Pull B", [
            VolumeMuscle.BACK, VolumeMuscle.BICEPS,
            VolumeMuscle.SIDE_REAR_DELTS,
        ]),
        SessionTemplate("Day 6 — Legs B", [
            VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
            VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS,
        ]),
    ]


SPLIT_RATIONALE = {
    3: "Full-body 3x/week distributes volume across sessions while respecting the per-session ceiling of ~6-8 direct sets per muscle.",
    4: "Upper/Lower 4x/week allows 6-10 sets per session per muscle with each muscle trained 2x/week — optimal for intermediates.",
    5: "Upper/Lower + PPL hybrid gives priority muscles 3x/week frequency while keeping per-session volume manageable.",
    6: "PPL 2x/week provides maximum frequency and volume distribution. Requires excellent recovery (sleep, nutrition, low stress).",
}


def plan_frequency(
    profile: UserProfile,
    volume_targets: list[VolumeTarget],
) -> SplitPlan:
    """Select a split based on available training days."""
    days = profile.days_per_week

    # Clamp to supported range
    if days <= 3:
        days = 3
    elif days >= 6:
        days = 6

    if days == 3:
        sessions = _full_body_3()
    elif days == 4:
        sessions = _upper_lower_4()
    elif days == 5:
        sessions = _ul_ppl_5(profile)
    else:
        sessions = _ppl_6()

    names = {3: "Full Body", 4: "Upper/Lower", 5: "UL/PPL Hybrid", 6: "PPL"}

    return SplitPlan(
        name=names[days],
        sessions=sessions,
        rationale=SPLIT_RATIONALE[days],
    )
