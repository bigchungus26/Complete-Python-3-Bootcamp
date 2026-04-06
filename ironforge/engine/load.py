"""Load, RIR, and rest period assignment."""

from ironforge.data.muscle_groups import Tier, TrainingLevel, Sex
from ironforge.data.constants import (
    REP_RANGES, REP_RANGES_FEMALE, RIR_BY_WEEK, RIR_BEGINNER, REST_PERIODS,
)
from ironforge.program.models import LoadPrescription


def assign_loading(
    tier: Tier,
    level: TrainingLevel,
    sex: Sex,
    week: int = 1,
    sets: int = 3,
) -> LoadPrescription:
    """Create a LoadPrescription for a given exercise tier and context."""
    ranges = REP_RANGES_FEMALE if sex == Sex.FEMALE else REP_RANGES
    rep_low, rep_high = ranges[tier]

    # RIR drops across the mesocycle: week 1=3, week 2=2, week 3=2, week 4=1
    if level == TrainingLevel.BEGINNER:
        rir = max(RIR_BEGINNER, RIR_BY_WEEK.get(week, 2))
    else:
        rir = RIR_BY_WEEK.get(week, 2)

    # T1 compounds get +1 RIR buffer in week 1
    if tier == Tier.T1 and week == 1:
        rir = min(rir + 1, 4)

    rest_low, rest_high = REST_PERIODS[tier]

    return LoadPrescription(
        sets=sets,
        rep_low=rep_low,
        rep_high=rep_high,
        rir=rir,
        rest_seconds=rest_high,
    )
