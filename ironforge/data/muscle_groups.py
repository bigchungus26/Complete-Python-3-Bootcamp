"""Enumerations for muscle groups, movement patterns, equipment, and training levels."""

from enum import Enum, auto


class MuscleGroup(Enum):
    CHEST_CLAVICULAR = auto()
    CHEST_STERNAL = auto()
    FRONT_DELT = auto()
    SIDE_DELT = auto()
    REAR_DELT = auto()
    TRICEPS_LONG = auto()
    TRICEPS_LATERAL = auto()
    BICEPS = auto()
    BRACHIALIS = auto()
    LATS = auto()
    MID_BACK = auto()
    LOWER_TRAP = auto()
    UPPER_TRAP = auto()
    QUADS = auto()
    HAMSTRINGS = auto()
    GLUTES = auto()
    CALVES = auto()
    ABS = auto()
    ADDUCTORS = auto()
    ABDUCTORS = auto()
    FOREARMS = auto()
    SPINAL_ERECTORS = auto()


# Aggregate groups used in volume landmark tables
class VolumeMuscle(Enum):
    QUADS = auto()
    CHEST = auto()
    BACK = auto()
    BICEPS = auto()
    SIDE_REAR_DELTS = auto()
    HAMSTRINGS = auto()
    TRICEPS = auto()
    CALVES = auto()
    GLUTES = auto()
    ABS = auto()
    FOREARMS = auto()


# Which detailed MuscleGroups roll up into each VolumeMuscle
VOLUME_MUSCLE_MAP: dict[VolumeMuscle, list[MuscleGroup]] = {
    VolumeMuscle.QUADS: [MuscleGroup.QUADS],
    VolumeMuscle.CHEST: [MuscleGroup.CHEST_CLAVICULAR, MuscleGroup.CHEST_STERNAL],
    VolumeMuscle.BACK: [MuscleGroup.LATS, MuscleGroup.MID_BACK],
    VolumeMuscle.BICEPS: [MuscleGroup.BICEPS],
    VolumeMuscle.SIDE_REAR_DELTS: [MuscleGroup.SIDE_DELT, MuscleGroup.REAR_DELT],
    VolumeMuscle.HAMSTRINGS: [MuscleGroup.HAMSTRINGS],
    VolumeMuscle.TRICEPS: [MuscleGroup.TRICEPS_LONG, MuscleGroup.TRICEPS_LATERAL],
    VolumeMuscle.CALVES: [MuscleGroup.CALVES],
    VolumeMuscle.GLUTES: [MuscleGroup.GLUTES],
    VolumeMuscle.ABS: [MuscleGroup.ABS],
    VolumeMuscle.FOREARMS: [MuscleGroup.FOREARMS],
}


class MovementPattern(Enum):
    SQUAT = auto()
    HIP_HINGE = auto()
    HORIZONTAL_PUSH = auto()
    HORIZONTAL_PULL = auto()
    VERTICAL_PUSH = auto()
    VERTICAL_PULL = auto()
    KNEE_FLEXION = auto()
    KNEE_EXTENSION = auto()
    ISOLATION = auto()


class TrainingLevel(Enum):
    BEGINNER = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()


class Equipment(Enum):
    BARBELL = auto()
    DUMBBELL = auto()
    CABLE = auto()
    MACHINE = auto()
    SMITH_MACHINE = auto()
    BODYWEIGHT = auto()
    EZ_BAR = auto()


class Tier(Enum):
    T1 = 1
    T2 = 2
    T3 = 3


class Goal(Enum):
    HYPERTROPHY = auto()
    STRENGTH = auto()
    HYBRID = auto()
    RECOMP = auto()


class Sex(Enum):
    MALE = auto()
    FEMALE = auto()


class CaloricPhase(Enum):
    SURPLUS = auto()
    DEFICIT = auto()
    MAINTENANCE = auto()


class EquipmentAccess(Enum):
    FULL_GYM = auto()
    LIMITED_GYM = auto()
    HOME_GYM = auto()
    OTHER = auto()
