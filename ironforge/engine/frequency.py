"""Frequency planner — determines split structure and session templates.

RULE: No muscle group may appear on two consecutive training days.
Full-body splits are the exception — they require rest days between sessions.
"""

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
    key: str
    name: str
    sessions: list[SessionTemplate]
    rationale: str
    requires_rest_days: bool = False  # True for full-body (non-consecutive days)


# ─── Muscle group building blocks ─────────────────────────────────────────────
# These are defined so that NO two adjacent blocks in any split share a muscle.
#
# The key fix: SIDE_REAR_DELTS lives on Push (side delt focus) only.
# Pull gets rear delt volume indirectly from rows (chest-supported flared rows,
# wide-grip cable rows all count toward rear delt volume per the algorithm rules).

UPPER = [VolumeMuscle.CHEST, VolumeMuscle.BACK, VolumeMuscle.SIDE_REAR_DELTS,
         VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS]
LOWER = [VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS, VolumeMuscle.GLUTES,
         VolumeMuscle.CALVES, VolumeMuscle.ABS]

# Push: chest, side/rear delts, triceps
# Pull: back, biceps (NO delts — rear delts get indirect row volume)
PUSH = [VolumeMuscle.CHEST, VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.TRICEPS]
PULL = [VolumeMuscle.BACK, VolumeMuscle.BICEPS]

LEGS = [VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS, VolumeMuscle.GLUTES,
        VolumeMuscle.CALVES, VolumeMuscle.ABS]

# Posterior / Anterior
POSTERIOR = [VolumeMuscle.BACK, VolumeMuscle.SIDE_REAR_DELTS,
             VolumeMuscle.HAMSTRINGS, VolumeMuscle.GLUTES, VolumeMuscle.CALVES]
ANTERIOR = [VolumeMuscle.CHEST, VolumeMuscle.QUADS,
            VolumeMuscle.TRICEPS, VolumeMuscle.BICEPS, VolumeMuscle.ABS]

# Upper/Lower crossed with Posterior/Anterior
UPPER_POSTERIOR = [VolumeMuscle.BACK, VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS]
LOWER_ANTERIOR = [VolumeMuscle.QUADS, VolumeMuscle.ABS, VolumeMuscle.CALVES]
UPPER_ANTERIOR = [VolumeMuscle.CHEST, VolumeMuscle.TRICEPS]
LOWER_POSTERIOR = [VolumeMuscle.HAMSTRINGS, VolumeMuscle.GLUTES]

# Torso / Limbs
TORSO = [VolumeMuscle.CHEST, VolumeMuscle.BACK,
         VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.ABS]
LIMBS = [VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS,
         VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
         VolumeMuscle.GLUTES, VolumeMuscle.CALVES]


def _has_consecutive_overlap(sessions: list[SessionTemplate]) -> bool:
    """Check that no muscle appears on two adjacent days."""
    for i in range(len(sessions) - 1):
        a = set(sessions[i].muscle_focus)
        b = set(sessions[i + 1].muscle_focus)
        if a & b:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════
#  3-DAY SPLITS
# ═══════════════════════════════════════════════════════════════════════

def _full_body_3() -> SplitPlan:
    ALL = UPPER + [VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
                   VolumeMuscle.CALVES]
    return SplitPlan(
        key="full_body_3", name="Full Body",
        requires_rest_days=True,
        rationale="Full-body 3x/week (e.g. Mon/Wed/Fri with rest days between). "
                  "Distributes volume across sessions — requires at least 1 rest day between sessions.",
        sessions=[
            SessionTemplate("Day 1 — Full Body A", ALL + [VolumeMuscle.GLUTES]),
            SessionTemplate("Day 2 — Full Body B", ALL + [VolumeMuscle.ABS]),
            SessionTemplate("Day 3 — Full Body C", ALL + [VolumeMuscle.GLUTES, VolumeMuscle.ABS]),
        ],
    )

def _push_pull_legs_3() -> SplitPlan:
    # Push → Pull → Legs: no overlap (delts only on Push)
    return SplitPlan(
        key="ppl_3", name="Push / Pull / Legs",
        rationale="PPL 1x/week. Each muscle hit once per week — minimum effective frequency. "
                  "No consecutive muscle overlap.",
        sessions=[
            SessionTemplate("Day 1 — Push", PUSH),
            SessionTemplate("Day 2 — Pull", PULL),
            SessionTemplate("Day 3 — Legs", LEGS),
        ],
    )

def _upper_lower_full_3() -> SplitPlan:
    # Upper → Full → Lower: no overlap if Full is between them
    # BUT Full overlaps with both Upper and Lower.
    # Fix: reorder to Upper → Lower → Full with rest days required
    return SplitPlan(
        key="ulf_3", name="Upper / Lower / Full",
        requires_rest_days=True,
        rationale="Upper-Lower-Full gives priority muscles an extra hit. "
                  "Requires rest days between sessions (e.g. Mon/Wed/Fri).",
        sessions=[
            SessionTemplate("Day 1 — Upper", UPPER),
            SessionTemplate("Day 2 — Lower", LOWER),
            SessionTemplate("Day 3 — Full Body",
                            UPPER + [VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
                                     VolumeMuscle.GLUTES, VolumeMuscle.CALVES, VolumeMuscle.ABS]),
        ],
    )


# ═══════════════════════════════════════════════════════════════════════
#  4-DAY SPLITS
# ═══════════════════════════════════════════════════════════════════════

def _upper_lower_4() -> SplitPlan:
    # U→L→U→L: no overlap ✓
    return SplitPlan(
        key="ul_4", name="Upper / Lower",
        rationale="Upper/Lower 4x/week — each muscle 2x/week. No consecutive overlap. "
                  "Optimal for intermediates.",
        sessions=[
            SessionTemplate("Day 1 — Upper A", UPPER),
            SessionTemplate("Day 2 — Lower A", LOWER),
            SessionTemplate("Day 3 — Upper B", UPPER),
            SessionTemplate("Day 4 — Lower B", LOWER),
        ],
    )

def _push_pull_4() -> SplitPlan:
    # Push→Legs→Pull→Legs: interleave with legs to avoid Push→Pull overlap
    return SplitPlan(
        key="pp_4", name="Push / Legs / Pull / Legs",
        rationale="Push and Pull separated by Legs — eliminates the delt overlap problem. "
                  "Quads and hamstrings each hit 2x/week.",
        sessions=[
            SessionTemplate("Day 1 — Push", PUSH),
            SessionTemplate("Day 2 — Legs A", LEGS),
            SessionTemplate("Day 3 — Pull", PULL),
            SessionTemplate("Day 4 — Legs B", LEGS),
        ],
    )

def _full_body_4() -> SplitPlan:
    ALL = UPPER + [VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS,
                   VolumeMuscle.CALVES]
    return SplitPlan(
        key="fb_4", name="Full Body (x4)",
        requires_rest_days=True,
        rationale="Full body 4x/week (e.g. Mon/Tue/Thu/Fri). Maximizes frequency. "
                  "Requires rest days between sessions — never run consecutive days.",
        sessions=[
            SessionTemplate("Day 1 — Full Body A", ALL + [VolumeMuscle.GLUTES]),
            SessionTemplate("Day 2 — Full Body B", ALL + [VolumeMuscle.ABS]),
            SessionTemplate("Day 3 — Full Body C", ALL + [VolumeMuscle.GLUTES]),
            SessionTemplate("Day 4 — Full Body D", ALL + [VolumeMuscle.ABS]),
        ],
    )

def _upper_lower_push_pull_4() -> SplitPlan:
    # Upper→Lower→Push→Pull: Lower→Push had CALVES overlap, Push→Pull had DELTS overlap
    # Fix: remove CALVES from Push, delts already only on Push not Pull
    return SplitPlan(
        key="ulpp_4", name="Upper / Lower / Push / Pull",
        rationale="Hybrid 4-day: Upper/Lower for compound focus, then Push/Pull for isolation. "
                  "No consecutive muscle overlap.",
        sessions=[
            SessionTemplate("Day 1 — Upper", UPPER),
            SessionTemplate("Day 2 — Lower", LOWER),
            SessionTemplate("Day 3 — Push", PUSH),  # no calves (was on Lower)
            SessionTemplate("Day 4 — Pull", PULL + [VolumeMuscle.HAMSTRINGS, VolumeMuscle.ABS]),
        ],
    )

def _post_ant_4() -> SplitPlan:
    # Post→Ant→Post→Ant: no overlap ✓
    return SplitPlan(
        key="pa_4", name="Posterior / Anterior (x2)",
        rationale="Posterior/Anterior groups muscles by chain. Posterior = back, delts, "
                  "hamstrings, glutes, calves. Anterior = chest, quads, triceps, biceps, abs. "
                  "No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Posterior A", POSTERIOR),
            SessionTemplate("Day 2 — Anterior A", ANTERIOR),
            SessionTemplate("Day 3 — Posterior B", POSTERIOR),
            SessionTemplate("Day 4 — Anterior B", ANTERIOR),
        ],
    )

def _upper_post_lower_ant_4() -> SplitPlan:
    # UP→LA→UA→LP: no overlap ✓
    return SplitPlan(
        key="upla_4", name="Upper Post / Lower Ant / Upper Ant / Lower Post",
        rationale="Crosses upper-lower and posterior-anterior axes. No two consecutive "
                  "sessions share any muscle group. Distributes fatigue uniquely.",
        sessions=[
            SessionTemplate("Day 1 — Upper Posterior", UPPER_POSTERIOR),
            SessionTemplate("Day 2 — Lower Anterior", LOWER_ANTERIOR),
            SessionTemplate("Day 3 — Upper Anterior", UPPER_ANTERIOR),
            SessionTemplate("Day 4 — Lower Posterior", LOWER_POSTERIOR),
        ],
    )

def _torso_limbs_4() -> SplitPlan:
    # T→L→T→L: no overlap ✓
    return SplitPlan(
        key="tl_4", name="Torso / Limbs (x2)",
        rationale="Torso = chest, back, shoulders, abs. Limbs = arms, quads, hamstrings, "
                  "glutes, calves. No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Torso A", TORSO),
            SessionTemplate("Day 2 — Limbs A", LIMBS),
            SessionTemplate("Day 3 — Torso B", TORSO),
            SessionTemplate("Day 4 — Limbs B", LIMBS),
        ],
    )


# ═══════════════════════════════════════════════════════════════════════
#  5-DAY SPLITS
# ═══════════════════════════════════════════════════════════════════════

def _ul_ppl_5() -> SplitPlan:
    # Upper→Lower→Push→Pull→Legs
    # Push→Pull had delts overlap. Fixed: delts only on Push.
    return SplitPlan(
        key="ulppl_5", name="Upper / Lower / Push / Pull / Legs",
        rationale="UL + PPL hybrid. Priority muscles get 3x/week. "
                  "No consecutive muscle overlap.",
        sessions=[
            SessionTemplate("Day 1 — Upper", UPPER),
            SessionTemplate("Day 2 — Lower", LOWER),
            SessionTemplate("Day 3 — Push", PUSH),
            SessionTemplate("Day 4 — Pull", PULL),
            SessionTemplate("Day 5 — Legs", LEGS),
        ],
    )

def _ppl_ul_5() -> SplitPlan:
    # Push→Pull→Legs→Upper→Lower
    # Push→Pull had delts overlap. Fixed: delts only on Push.
    return SplitPlan(
        key="pplul_5", name="Push / Pull / Legs / Upper / Lower",
        rationale="PPL then UL — every muscle at least 2x/week, upper body 3x. "
                  "No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Push", PUSH),
            SessionTemplate("Day 2 — Pull", PULL),
            SessionTemplate("Day 3 — Legs", LEGS),
            SessionTemplate("Day 4 — Upper", UPPER),
            SessionTemplate("Day 5 — Lower", LOWER),
        ],
    )

def _upper_lower_push_lower_pull_5() -> SplitPlan:
    # Was Upper/Lower/Legs/Upper/Lower which had Lower→Legs full overlap
    # Redesigned: Upper→Lower→Push→Legs→Pull — all distinct adjacent pairs
    return SplitPlan(
        key="ulplp_5", name="Upper / Lower / Push / Legs / Pull",
        rationale="5-day alternating split. Each session is distinct from its neighbors. "
                  "Legs 2x, upper body push/pull 2x each. No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Upper", UPPER),
            SessionTemplate("Day 2 — Lower", LOWER),
            SessionTemplate("Day 3 — Push", PUSH),
            SessionTemplate("Day 4 — Legs", LEGS),
            SessionTemplate("Day 5 — Pull", PULL),
        ],
    )

def _arnold_5() -> SplitPlan:
    # CB→SA→L→CB→SA+L: all adjacent pairs are distinct ✓
    return SplitPlan(
        key="arnold_5", name="Chest+Back / Shoulders+Arms / Legs (x2-ish)",
        rationale="Arnold-style: chest+back supersetted, shoulders+arms, legs. "
                  "Each hit ~2x/week. No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Chest + Back",
                            [VolumeMuscle.CHEST, VolumeMuscle.BACK]),
            SessionTemplate("Day 2 — Shoulders + Arms",
                            [VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
                             VolumeMuscle.TRICEPS]),
            SessionTemplate("Day 3 — Legs A", LEGS),
            SessionTemplate("Day 4 — Chest + Back",
                            [VolumeMuscle.CHEST, VolumeMuscle.BACK]),
            SessionTemplate("Day 5 — Shoulders + Arms + Legs",
                            [VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
                             VolumeMuscle.TRICEPS, VolumeMuscle.QUADS,
                             VolumeMuscle.HAMSTRINGS, VolumeMuscle.CALVES]),
        ],
    )

def _bro_5() -> SplitPlan:
    # Was Chest/Back/Shoulders/Arms/Legs — Shoulders→Arms had TRICEPS overlap
    # Fix: reorder to Chest/Back/Arms/Shoulders/Legs — no overlap
    return SplitPlan(
        key="bro_5", name="Chest / Back / Arms / Shoulders / Legs",
        rationale="Classic body-part split reordered: arms between back and shoulders "
                  "to eliminate consecutive triceps overlap. Each muscle 1x/week with "
                  "high per-session volume.",
        sessions=[
            SessionTemplate("Day 1 — Chest",
                            [VolumeMuscle.CHEST]),
            SessionTemplate("Day 2 — Back",
                            [VolumeMuscle.BACK]),
            SessionTemplate("Day 3 — Arms",
                            [VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS,
                             VolumeMuscle.FOREARMS]),
            SessionTemplate("Day 4 — Shoulders",
                            [VolumeMuscle.SIDE_REAR_DELTS]),
            SessionTemplate("Day 5 — Legs", LEGS),
        ],
    )


# ═══════════════════════════════════════════════════════════════════════
#  6-DAY SPLITS
# ═══════════════════════════════════════════════════════════════════════

def _ppl_6() -> SplitPlan:
    # Push→Pull→Legs x2: Push→Pull had delts. Fixed: delts only on Push.
    return SplitPlan(
        key="ppl_6", name="PPL (x2)",
        rationale="PPL 2x/week. Maximum frequency and volume distribution. "
                  "No consecutive overlap. Requires excellent recovery.",
        sessions=[
            SessionTemplate("Day 1 — Push A", PUSH),
            SessionTemplate("Day 2 — Pull A", PULL),
            SessionTemplate("Day 3 — Legs A", LEGS),
            SessionTemplate("Day 4 — Push B", PUSH),
            SessionTemplate("Day 5 — Pull B", PULL),
            SessionTemplate("Day 6 — Legs B", LEGS),
        ],
    )

def _arnold_6() -> SplitPlan:
    # CB→SA→L x2: all adjacent distinct ✓
    return SplitPlan(
        key="arnold_6", name="Arnold Split (x2)",
        rationale="Arnold split 2x/week: chest+back, shoulders+arms, legs. "
                  "High frequency, no consecutive overlap. Advanced only.",
        sessions=[
            SessionTemplate("Day 1 — Chest + Back A",
                            [VolumeMuscle.CHEST, VolumeMuscle.BACK]),
            SessionTemplate("Day 2 — Shoulders + Arms A",
                            [VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
                             VolumeMuscle.TRICEPS]),
            SessionTemplate("Day 3 — Legs A", LEGS),
            SessionTemplate("Day 4 — Chest + Back B",
                            [VolumeMuscle.CHEST, VolumeMuscle.BACK]),
            SessionTemplate("Day 5 — Shoulders + Arms B",
                            [VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BICEPS,
                             VolumeMuscle.TRICEPS]),
            SessionTemplate("Day 6 — Legs B", LEGS),
        ],
    )

def _ul_3x_6() -> SplitPlan:
    # U→L x3: no overlap ✓
    return SplitPlan(
        key="ul3_6", name="Upper / Lower (x3)",
        rationale="Upper/Lower 3x each — every muscle trained 3x/week. "
                  "No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Upper A", UPPER),
            SessionTemplate("Day 2 — Lower A", LOWER),
            SessionTemplate("Day 3 — Upper B", UPPER),
            SessionTemplate("Day 4 — Lower B", LOWER),
            SessionTemplate("Day 5 — Upper C", UPPER),
            SessionTemplate("Day 6 — Lower C", LOWER),
        ],
    )

def _ppl_arnold_6() -> SplitPlan:
    # Was PPL + specialization with multiple overlaps.
    # Redesigned: PPL + Arnold (CB/SA/L) — all adjacent pairs distinct
    return SplitPlan(
        key="hybrid_6", name="Push / Pull / Legs / Chest+Back / Arms+Delts / Legs",
        rationale="PPL first half, Arnold-style second half. Every muscle 2x/week, "
                  "no consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Push", PUSH),
            SessionTemplate("Day 2 — Pull", PULL),
            SessionTemplate("Day 3 — Legs A", LEGS),
            SessionTemplate("Day 4 — Chest + Back",
                            [VolumeMuscle.CHEST, VolumeMuscle.BACK]),
            SessionTemplate("Day 5 — Arms + Delts",
                            [VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS,
                             VolumeMuscle.SIDE_REAR_DELTS]),
            SessionTemplate("Day 6 — Legs B", LEGS),
        ],
    )

def _post_ant_6() -> SplitPlan:
    # Post→Ant x3: no overlap ✓
    return SplitPlan(
        key="pa_6", name="Posterior / Anterior (x3)",
        rationale="Posterior/Anterior 3x each — 3x/week per chain. "
                  "No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Posterior A", POSTERIOR),
            SessionTemplate("Day 2 — Anterior A", ANTERIOR),
            SessionTemplate("Day 3 — Posterior B", POSTERIOR),
            SessionTemplate("Day 4 — Anterior B", ANTERIOR),
            SessionTemplate("Day 5 — Posterior C", POSTERIOR),
            SessionTemplate("Day 6 — Anterior C", ANTERIOR),
        ],
    )

def _torso_limbs_6() -> SplitPlan:
    # T→L x3: no overlap ✓
    return SplitPlan(
        key="tl_6", name="Torso / Limbs (x3)",
        rationale="Torso/Limbs 3x each — maximum frequency. "
                  "No consecutive overlap.",
        sessions=[
            SessionTemplate("Day 1 — Torso A", TORSO),
            SessionTemplate("Day 2 — Limbs A", LIMBS),
            SessionTemplate("Day 3 — Torso B", TORSO),
            SessionTemplate("Day 4 — Limbs B", LIMBS),
            SessionTemplate("Day 5 — Torso C", TORSO),
            SessionTemplate("Day 6 — Limbs C", LIMBS),
        ],
    )


# ═══════════════════════════════════════════════════════════════════════
#  REGISTRY
# ═══════════════════════════════════════════════════════════════════════

SPLITS_BY_DAYS: dict[int, list[SplitPlan]] = {
    3: [_full_body_3(), _push_pull_legs_3(), _upper_lower_full_3()],
    4: [_upper_lower_4(), _push_pull_4(), _full_body_4(), _upper_lower_push_pull_4(),
        _post_ant_4(), _upper_post_lower_ant_4(), _torso_limbs_4()],
    5: [_ul_ppl_5(), _ppl_ul_5(), _upper_lower_push_lower_pull_5(),
        _arnold_5(), _bro_5()],
    6: [_ppl_6(), _arnold_6(), _ul_3x_6(), _ppl_arnold_6(),
        _post_ant_6(), _torso_limbs_6()],
}

# Flat lookup
ALL_SPLITS: dict[str, SplitPlan] = {}
for splits in SPLITS_BY_DAYS.values():
    for s in splits:
        ALL_SPLITS[s.key] = s


def get_split_options(days: int) -> list[SplitPlan]:
    """Return all available split options for the given number of days."""
    days = max(3, min(6, days))
    return SPLITS_BY_DAYS[days]


def plan_frequency(
    profile: UserProfile,
    volume_targets: list[VolumeTarget],
    split_key: str | None = None,
) -> SplitPlan:
    """Select a split based on available training days and optional key."""
    days = max(3, min(6, profile.days_per_week))
    if split_key and split_key in ALL_SPLITS:
        return ALL_SPLITS[split_key]
    return SPLITS_BY_DAYS[days][0]
