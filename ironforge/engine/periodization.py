"""Mesocycle structure, progression models, and deload logic."""

from ironforge.data.muscle_groups import TrainingLevel, Goal, CaloricPhase
from ironforge.data.constants import DELOAD_FREQUENCY
from ironforge.intake.profile import UserProfile
from ironforge.program.models import MesocycleOverview


def build_mesocycle_overview(
    profile: UserProfile,
    levels: dict,
) -> list[MesocycleOverview]:
    """Build the 4-week mesocycle overview. Deload is reactive, not scheduled."""
    return [
        MesocycleOverview(
            week=1,
            volume_description="Same sets as programmed",
            rir="3-4 RIR",
            load_note="Establish working weights",
        ),
        MesocycleOverview(
            week=2,
            volume_description="Same sets",
            rir="2-3 RIR",
            load_note="Attempt +2.5-5 lbs if top of rep range hit",
        ),
        MesocycleOverview(
            week=3,
            volume_description="Same sets",
            rir="2 RIR",
            load_note="Attempt +2.5-5 lbs if top of rep range hit",
        ),
        MesocycleOverview(
            week=4,
            volume_description="Same sets",
            rir="1-2 RIR",
            load_note="Push hard — last week before reassessment",
        ),
    ]


def build_progression_instructions(
    profile: UserProfile,
    levels: dict,
) -> str:
    """Generate progression instructions based on training level."""
    overall = profile.overall_level
    goal = profile.primary_goal

    sections: list[str] = []

    if overall == TrainingLevel.BEGINNER:
        sections.append(
            "LINEAR PROGRESSION:\n"
            "- Add weight every 1-2 sessions\n"
            "- Compounds: +5-10 lbs/session; Isolations: +2.5-5 lbs\n"
            "- When you cannot add weight for 3 consecutive sessions on a lift, "
            "switch to double progression for that lift\n"
            "- Track RIR passively — do not use for load prescription yet\n"
            "- Volume: maintain 10-15 hard sets/muscle/week"
        )
    elif overall == TrainingLevel.INTERMEDIATE:
        sections.append(
            "DOUBLE PROGRESSION:\n"
            "- Each exercise has a rep range (e.g., 3x8-12)\n"
            "- Start at the bottom of the range with a challenging weight\n"
            "- Add reps each session until you hit the top of the range on ALL sets\n"
            "- Then add weight (+5 lbs compounds, +2.5 lbs isolations) and drop "
            "back to the bottom of the range\n"
            "- Expected load increase: every ~3-5 sessions\n"
            "- Volume: 12-20 hard sets/muscle/week"
        )
    else:
        sections.append(
            "PERIODIZED AUTOREGULATION:\n"
            "- Use the prescribed RIR targets to autoregulate load\n"
            "- Within a mesocycle: increase load when you achieve the top of the "
            "rep range at the target RIR on set 1\n"
            "- Primary overload lever = adding sets week to week\n"
            "- Secondary lever = adding load while maintaining rep range\n"
            "- After 2-4 consecutive hypertrophy mesocycles: run a 2-4 week "
            "maintenance phase (~6 sets/muscle/week), then restart at MEV\n"
            "- Volume: 10-20 hard sets/muscle/week (quality > quantity)"
        )

    # Universal rules
    sections.append(
        "\nUNIVERSAL RULES:\n"
        "- Across mesocycles: start next block 1-2 sets/muscle higher than "
        "previous starting point\n"
        "- Add 2.5-5 lbs to compounds, 2.5 lbs to isolations at start of each new block\n"
        "- Keep 60-70% of program identical between mesocycles; rotate 30-40%\n"
        "- Reset RIR to 3-4 in Week 1 of every new mesocycle\n"
        "- A true plateau requires 4+ weeks of stalled progress to diagnose — "
        "do not change programming after 1-2 bad sessions"
    )

    if goal in (Goal.STRENGTH, Goal.HYBRID):
        sections.append(
            "\nSTRENGTH NOTES:\n"
            "- Prioritize load on the bar for main compounds\n"
            "- Include 1 strength-emphasis mesocycle (5-8 rep focus) per macrocycle"
        )

    return "\n".join(sections)


def build_deload_instructions(profile: UserProfile) -> str:
    """Generate deload instructions based on training level."""
    overall = profile.overall_level
    freq = DELOAD_FREQUENCY[overall]

    lines = [
        "ACTIVE DELOAD PROTOCOL (never take full rest weeks):",
        f"- Frequency: every {freq[0]}-{freq[1]} weeks, or when 2+ reactive triggers appear",
        "- Cut volume 40-60% (drop sets, not load)",
        "- Reduce load ~10% OR add 2-3 RIR to all exercises",
        "- Maintain frequency — keep all training days",
        "- Drop accessories, keep main compounds",
        "",
        "REACTIVE DELOAD TRIGGERS (deload when 2+ present):",
        "- Performance drop >5% across 2+ consecutive sessions",
        "- Persistent soreness still present when retraining the same muscle",
        "- Rising session RPE at stable volume for 2+ weeks",
        "- Joint pain escalating session to session",
        "- Loss of motivation / dreading training",
        "- Appetite suppression during a hard training block",
        "",
        "NUCKOLS RULE: Schedule a deload after your BEST sessions too — a huge",
        "PR means you dug very deep, and failing to pull back often leads to",
        "significant regression the following week.",
    ]

    if profile.caloric_phase == CaloricPhase.DEFICIT:
        lines.append(
            "\nDEFICIT NOTE: Deload same frequency or more often. Recovery is "
            "impaired — err on the side of deloading earlier."
        )

    return "\n".join(lines)
