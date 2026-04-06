"""User profile dataclass — the contract between intake and engine."""

from dataclasses import dataclass, field
from ironforge.data.muscle_groups import (
    Goal, Sex, CaloricPhase, EquipmentAccess, Equipment,
    MovementPattern, TrainingLevel, VolumeMuscle,
)


@dataclass
class UserProfile:
    # Goals
    primary_goal: Goal = Goal.HYPERTROPHY
    priority_muscles: list[VolumeMuscle] = field(default_factory=list)
    caloric_phase: CaloricPhase = CaloricPhase.MAINTENANCE

    # Training history
    training_months: int = 0
    pattern_experience: dict[MovementPattern, TrainingLevel] = field(default_factory=dict)
    can_add_weight_every_session: bool = False
    adds_weight_every_1_2_weeks: bool = False

    # Schedule
    days_per_week: int = 4
    session_minutes: int = 60
    prefers_supersets: bool = True

    # Equipment
    equipment_access: EquipmentAccess = EquipmentAccess.FULL_GYM
    available_equipment: set[Equipment] = field(default_factory=lambda: {
        Equipment.BARBELL, Equipment.DUMBBELL, Equipment.CABLE,
        Equipment.MACHINE, Equipment.SMITH_MACHINE, Equipment.EZ_BAR,
        Equipment.BODYWEIGHT,
    })

    # Individual
    sex: Sex = Sex.MALE
    injuries: list[str] = field(default_factory=list)
    current_sets_per_muscle: int = 0
    current_program: str = "starting fresh"
    wants_glute_focus: bool = False

    @property
    def overall_level(self) -> TrainingLevel:
        """Most common training level across patterns, for general decisions."""
        if not self.pattern_experience:
            if self.training_months < 6:
                return TrainingLevel.BEGINNER
            elif self.training_months < 36:
                return TrainingLevel.INTERMEDIATE
            return TrainingLevel.ADVANCED
        levels = list(self.pattern_experience.values())
        from collections import Counter
        return Counter(levels).most_common(1)[0][0]
