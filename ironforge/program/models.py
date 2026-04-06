"""Program data models — the complete program representation."""

from dataclasses import dataclass, field
from ironforge.data.exercises import ExerciseDefinition
from ironforge.data.muscle_groups import (
    MuscleGroup, MovementPattern, TrainingLevel, Tier, VolumeMuscle,
)


@dataclass
class LoadPrescription:
    sets: int
    rep_low: int
    rep_high: int
    rir: int
    rest_seconds: int


@dataclass
class ProgrammedExercise:
    exercise: ExerciseDefinition
    load: LoadPrescription
    tier: Tier
    notes: str = ""
    superset_pair_id: int | None = None


@dataclass
class ProgramSession:
    day_label: str
    exercises: list[ProgrammedExercise] = field(default_factory=list)


@dataclass
class ProgramWeek:
    week_number: int
    sessions: list[ProgramSession] = field(default_factory=list)


@dataclass
class VolumeTarget:
    muscle: VolumeMuscle
    mev: float
    working: float  # programmed sets for week 1
    mrv: float


@dataclass
class MesocycleOverview:
    week: int
    volume_description: str
    rir: str
    load_note: str


@dataclass
class Program:
    # Section 1
    level_assessment: dict[MovementPattern, TrainingLevel]
    # Section 2
    volume_targets: list[VolumeTarget]
    # Section 3
    split_name: str
    split_rationale: str
    # Section 4
    week1: ProgramWeek
    # Section 5
    progression_instructions: str
    # Section 6
    deload_instructions: str
    # Section 7
    mesocycle_overview: list[MesocycleOverview]
