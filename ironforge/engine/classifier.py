"""Training level classification per movement pattern."""

from ironforge.data.muscle_groups import MovementPattern, TrainingLevel
from ironforge.intake.profile import UserProfile


# Default patterns to classify
CORE_PATTERNS = [
    MovementPattern.SQUAT,
    MovementPattern.HIP_HINGE,
    MovementPattern.HORIZONTAL_PUSH,
    MovementPattern.VERTICAL_PULL,
    MovementPattern.HORIZONTAL_PULL,
    MovementPattern.VERTICAL_PUSH,
]


def classify(profile: UserProfile) -> dict[MovementPattern, TrainingLevel]:
    """Determine training level per movement pattern based on intake answers."""
    result: dict[MovementPattern, TrainingLevel] = {}

    for pattern in CORE_PATTERNS:
        # If the user gave per-pattern answers, use those
        if pattern in profile.pattern_experience:
            result[pattern] = profile.pattern_experience[pattern]
            continue

        # Otherwise, infer from global training history
        if profile.training_months < 6:
            result[pattern] = TrainingLevel.BEGINNER
        elif profile.training_months < 36:
            # Check if they can still linearly progress
            if profile.can_add_weight_every_session:
                result[pattern] = TrainingLevel.BEGINNER
            elif profile.adds_weight_every_1_2_weeks:
                result[pattern] = TrainingLevel.INTERMEDIATE
            else:
                result[pattern] = TrainingLevel.INTERMEDIATE
        else:
            if profile.can_add_weight_every_session:
                result[pattern] = TrainingLevel.INTERMEDIATE
            elif profile.adds_weight_every_1_2_weeks:
                result[pattern] = TrainingLevel.INTERMEDIATE
            else:
                result[pattern] = TrainingLevel.ADVANCED

    return result
